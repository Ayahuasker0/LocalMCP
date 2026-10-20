package com.example.mcp;

import com.example.mcp.tools.GitTools;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class GitServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(GitServerApplication.class, args);
    }

    @Bean
    public ToolCallbackProvider gitToolCallbackProvider(
            GitTools gitTools
    ) {
        return MethodToolCallbackProvider.builder()
                .toolObjects(gitTools)
                .build();
    }
}
