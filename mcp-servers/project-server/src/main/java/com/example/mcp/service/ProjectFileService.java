package com.example.mcp.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.xml.XMLConstants;
import javax.xml.parsers.DocumentBuilderFactory;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Stream;

@Service
public class ProjectFileService {

    private static final int MAX_FILE_BYTES = 100_000;
    private static final int MAX_RESULTS = 50;
    private static final int MAX_SCANNED_FILES = 5_000;

    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(
            ".java", ".py", ".xml", ".yaml", ".yml",
            ".properties", ".json", ".md", ".txt",
            ".sql", ".gradle", ".kt"
    );

    private static final Set<String> EXCLUDED_DIRECTORIES = Set.of(
            ".git", ".idea", ".venv", "venv",
            "target", "build", "node_modules",
            "__pycache__", ".gradle"
    );

    private final Path root;

    public ProjectFileService(
            @Value("${project.root}") String rootPath
    ) throws IOException {

        this.root = Path.of(rootPath).toRealPath();

        if (!Files.isDirectory(root)) {
            throw new IllegalArgumentException(
                    "Project root must be a directory"
            );
        }
    }

    /**
     * Resolve a project-relative path.
     *
     * Reject absolute paths, traversal outside the root,
     * and symbolic links.
     */
    private Path resolve(String relativePath) throws IOException {

        Path requested = Path.of(relativePath);

        if (requested.isAbsolute()) {
            throw new IllegalArgumentException(
                    "Absolute paths are not allowed"
            );
        }

        Path candidate = root.resolve(requested).normalize();

        if (!candidate.startsWith(root)) {
            throw new SecurityException(
                    "Access outside project root is forbidden"
            );
        }

        Path current = root;

        for (Path part : root.relativize(candidate)) {
            current = current.resolve(part);

            if (Files.isSymbolicLink(current)) {
                throw new SecurityException(
                        "Symbolic links are not allowed"
                );
            }
        }

        return candidate;
    }

    private boolean isExcluded(Path path) {

        Path relative = root.relativize(path);

        for (Path part : relative) {
            if (EXCLUDED_DIRECTORIES.contains(part.toString())) {
                return true;
            }
        }

        return false;
    }

    private boolean isAllowedFile(Path path) {

        String name = path.getFileName()
                .toString()
                .toLowerCase(Locale.ROOT);

        if (name.equals("pom.xml")) {
            return true;
        }

        return ALLOWED_EXTENSIONS.stream()
                .anyMatch(name::endsWith);
    }

    private boolean isReadableSource(Path path)
            throws IOException {

        return Files.isRegularFile(
                    path,
                    LinkOption.NOFOLLOW_LINKS
                )
                && !isExcluded(path)
                && isAllowedFile(path)
                && Files.size(path) <= MAX_FILE_BYTES;
    }

    /**
     * List source files inside the project.
     */
    public List<String> listFiles() throws IOException {

        List<String> result = new ArrayList<>();

        try (Stream<Path> paths = Files.walk(root)) {

            Iterator<Path> iterator = paths
                    .filter(path -> !Files.isSymbolicLink(path))
                    .filter(path -> !isExcluded(path))
                    .filter(Files::isRegularFile)
                    .filter(this::isAllowedFile)
                    .iterator();

            while (iterator.hasNext()
                    && result.size() < MAX_RESULTS) {

                Path path = iterator.next();

                if (isReadableSource(path)) {
                    result.add(
                        root.relativize(path).toString()
                    );
                }
            }
        }

        return result;
    }

    /**
     * Read a project source file.
     */
    public String readFile(String relativePath)
            throws IOException {

        Path file = resolve(relativePath);

        if (!isReadableSource(file)) {
            throw new IllegalArgumentException(
                    "File is unavailable, excluded, or too large"
            );
        }

        return Files.readString(
                file,
                StandardCharsets.UTF_8
        );
    }

    /**
     * Search text in source files.
     */
    public List<Map<String, Object>> searchCode(
            String query
    ) throws IOException {

        if (query == null || query.isBlank()) {
            throw new IllegalArgumentException(
                    "Search query cannot be empty"
            );
        }

        List<Map<String, Object>> results = new ArrayList<>();
        int scanned = 0;

        try (Stream<Path> paths = Files.walk(root)) {

            Iterator<Path> iterator = paths
                    .filter(path -> !Files.isSymbolicLink(path))
                    .filter(path -> !isExcluded(path))
                    .filter(Files::isRegularFile)
                    .filter(this::isAllowedFile)
                    .iterator();

            while (iterator.hasNext()
                    && results.size() < MAX_RESULTS
                    && scanned < MAX_SCANNED_FILES) {

                Path file = iterator.next();
                scanned++;

                if (!isReadableSource(file)) {
                    continue;
                }

                List<String> lines = Files.readAllLines(
                        file,
                        StandardCharsets.UTF_8
                );

                for (int i = 0; i < lines.size(); i++) {

                    if (lines.get(i).contains(query)) {

                        Map<String, Object> match =
                                new LinkedHashMap<>();

                        match.put(
                            "file",
                            root.relativize(file).toString()
                        );

                        match.put("line", i + 1);
                        match.put(
                            "content",
                            lines.get(i)
                        );

                        results.add(match);

                        if (results.size() >= MAX_RESULTS) {
                            break;
                        }
                    }
                }
            }
        }

        return results;
    }

    /**
     * Read direct dependencies from a Maven pom.xml.
     */
    public List<Map<String, String>> getDependencies(
            String pomPath
    ) throws Exception {

        Path file = resolve(pomPath);

        if (!file.getFileName().toString().equals("pom.xml")
                || !isReadableSource(file)) {
            throw new IllegalArgumentException(
                    "A readable pom.xml is required"
            );
        }

        DocumentBuilderFactory factory =
                DocumentBuilderFactory.newInstance();

        // Prevent XML external entity attacks.
        factory.setFeature(
                "http://apache.org/xml/features/disallow-doctype-decl",
                true
        );

        factory.setFeature(
                "http://xml.org/sax/features/external-general-entities",
                false
        );

        factory.setFeature(
                "http://xml.org/sax/features/external-parameter-entities",
                false
        );

        factory.setFeature(
                XMLConstants.FEATURE_SECURE_PROCESSING,
                true
        );

        factory.setAttribute(
                XMLConstants.ACCESS_EXTERNAL_DTD,
                ""
        );

        factory.setAttribute(
                XMLConstants.ACCESS_EXTERNAL_SCHEMA,
                ""
        );

        Document document = factory
                .newDocumentBuilder()
                .parse(file.toFile());

        Element project = document.getDocumentElement();

        NodeList dependenciesContainers =
                project.getElementsByTagName("dependencies");

        List<Map<String, String>> result = new ArrayList<>();

        // Only direct project dependencies, not dependencyManagement.
        for (int i = 0; i < dependenciesContainers.getLength(); i++) {

            Element container =
                    (Element) dependenciesContainers.item(i);

            if (container.getParentNode() != project) {
                continue;
            }

            NodeList children = container.getChildNodes();

            for (int j = 0; j < children.getLength(); j++) {

                Node child = children.item(j);

                if (!(child instanceof Element dependency)
                        || !dependency.getTagName().equals("dependency")) {
                    continue;
                }

                Map<String, String> entry =
                        new LinkedHashMap<>();

                entry.put(
                    "groupId",
                    childText(dependency, "groupId")
                );

                entry.put(
                    "artifactId",
                    childText(dependency, "artifactId")
                );

                entry.put(
                    "version",
                    childText(dependency, "version")
                );

                entry.put(
                    "scope",
                    childText(dependency, "scope")
                );

                result.add(entry);
            }
        }

        return result;
    }

    private String childText(Element parent, String name) {

        NodeList children = parent.getChildNodes();

        for (int i = 0; i < children.getLength(); i++) {

            Node node = children.item(i);

            if (node instanceof Element element
                    && element.getTagName().equals(name)) {

                return element.getTextContent().trim();
            }
        }

        return "";
    }
}