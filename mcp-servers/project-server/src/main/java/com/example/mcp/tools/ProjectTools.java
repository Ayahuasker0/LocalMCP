package com.example.mcp.tools;

import com.example.mcp.service.ProjectFileService;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;

@Component
public class ProjectTools {

    private final ProjectFileService projectFileService;

    public ProjectTools(
            ProjectFileService projectFileService
    ) {
        this.projectFileService = projectFileService;
    }

    @Tool(
        name = "list_project_files",
        description = """
            Lists source files in the configured project.
            Returns project-relative file paths.
            """
    )
    public List<String> listProjectFiles() throws Exception {

        return projectFileService.listFiles();
    }

    @Tool(
        name = "read_project_file",
        description = """
            Reads a source file from the configured project.
            The path must be relative to the project root.
            """
    )
    public String readProjectFile(
            @ToolParam(
                description = "Project-relative file path"
            )
            String relativePath
    ) throws Exception {

        return projectFileService.readFile(relativePath);
    }

    @Tool(
        name = "search_project_code",
        description = """
            Searches source files for an exact, case-sensitive
            text substring. Returns matching files, line
            numbers, and source lines.
            """
    )
    public List<Map<String, Object>> searchProjectCode(
            @ToolParam(
                description = "Text to search for"
            )
            String query
    ) throws Exception {

        return projectFileService.searchCode(query);
    }

    @Tool(
        name = "get_project_dependencies",
        description = """
            Reads directly declared Maven dependencies
            from a specified pom.xml.
            Does not resolve transitive dependencies.
            """
    )
    public List<Map<String, String>> getProjectDependencies(
            @ToolParam(
                description = "Relative path to pom.xml"
            )
            String pomPath
    ) throws Exception {

        return projectFileService.getDependencies(pomPath);
    }
}