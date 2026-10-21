package com.example.mcp;

import com.example.mcp.tools.ProjectTools;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class ProjectServerApplication {

    public static void main(String[] args) {

        SpringApplication.run(
            ProjectServerApplication.class,
            args
        );
    }

    @Bean
    public ToolCallbackProvider projectToolCallbackProvider(
            ProjectTools projectTools
    ) {

        return MethodToolCallbackProvider.builder()
                .toolObjects(projectTools)
                .build();
    }
}