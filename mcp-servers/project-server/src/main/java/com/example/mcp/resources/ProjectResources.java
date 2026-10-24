package com.example.mcp.resources;

import com.example.mcp.service.ProjectFileService;
import org.springframework.ai.mcp.annotation.McpResource;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class ProjectResources {

    private final ProjectFileService files;

    public ProjectResources(ProjectFileService files) {
        this.files = files;
    }

    @McpResource(
        uri = "project://overview",
        name = "project-overview",
        description = "Overview of the configured source project",
        mimeType = "text/plain"
    )
    public String overview() throws Exception {
        List<String> paths = files.listFiles();

        return """
            Project overview

            Source files (up to 50):
            """ + String.join("\n", paths);
    }

    @McpResource(
        uri = "project://dependencies",
        name = "project-dependencies",
        description = "Maven dependencies of the project-server module",
        mimeType = "text/plain"
    )
    public String dependencies() throws Exception {
        return files.getDependencies(
                "mcp-servers/project-server/pom.xml"
        ).toString();
    }
}