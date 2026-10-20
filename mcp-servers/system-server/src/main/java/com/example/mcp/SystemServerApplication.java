package com.example.mcp;

import com.example.mcp.tools.CalculatorTools;
import com.example.mcp.tools.SystemTools;

import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import org.springframework.context.annotation.Bean;

@SpringBootApplication
public class SystemServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(
                SystemServerApplication.class,
                args
        );
    }

    @Bean
    public ToolCallbackProvider toolCallbackProvider(
            CalculatorTools calculatorTools,
            SystemTools systemTools
    ) {
        return MethodToolCallbackProvider.builder()
                .toolObjects(calculatorTools, systemTools)
                .build();
    }
}