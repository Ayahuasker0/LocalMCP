package com.example.mcp.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Map;

@Component
public class SystemTools {

    @Tool(
            name = "get_current_time",
            description = "Returns the current UTC time"
    )
    public String getCurrentTime() {
        return Instant.now().toString();
    }

    @Tool(
            name = "get_system_info",
            description = "Returns information about the operating system and Java runtime"
    )
    public Map<String, String> getSystemInfo() {
        return Map.of(
                "os", System.getProperty("os.name"),
                "osVersion", System.getProperty("os.version"),
                "javaVersion", System.getProperty("java.version"),
                "architecture", System.getProperty("os.arch")
        );
    }
}