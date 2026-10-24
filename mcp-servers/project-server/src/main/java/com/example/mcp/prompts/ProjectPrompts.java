package com.example.mcp.prompts;

import io.modelcontextprotocol.spec.McpSchema.GetPromptResult;
import io.modelcontextprotocol.spec.McpSchema.PromptMessage;
import io.modelcontextprotocol.spec.McpSchema.Role;
import io.modelcontextprotocol.spec.McpSchema.TextContent;

import org.springframework.ai.mcp.annotation.McpArg;
import org.springframework.ai.mcp.annotation.McpPrompt;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class ProjectPrompts {

    @McpPrompt(
        name = "review_java_class",
        description = "Review a Java class for bugs, security and design issues"
    )
    public GetPromptResult reviewJavaClass(
            @McpArg(
                name = "file_path",
                description = "Project-relative Java file path",
                required = true
            )
            String filePath
    ) {

        String instruction = """
            Perform a senior-level Java code review.

            Target file: %s

            First retrieve the file using read_project_file.

            Review:
            1. Correctness and possible bugs
            2. Exception handling
            3. Concurrency and thread safety
            4. Performance
            5. Security
            6. SOLID principles
            7. Testability

            For each issue provide:
            - Severity
            - File and line reference, when available
            - Explanation
            - Recommended fix

            Distinguish confirmed problems from potential risks.
            Do not invent source code or line numbers.
            """.formatted(filePath);

        return userPrompt(
            "Java code review",
            instruction
        );
    }

    @McpPrompt(
        name = "analyze_performance",
        description = "Investigate performance problems in a Java module"
    )
    public GetPromptResult analyzePerformance(
            @McpArg(
                name = "module",
                description = "Project module or package to analyze",
                required = true
            )
            String module
    ) {

        String instruction = """
            Investigate potential performance problems.

            Target module: %s

            Use available project tools to inspect relevant code.

            Focus on:
            1. N+1 database queries
            2. Inefficient collection operations
            3. Excessive object allocation
            4. Blocking I/O
            5. Missing pagination
            6. Expensive database operations
            7. Cache usage
            8. Unnecessary repeated computations

            Provide:
            - Findings supported by retrieved code
            - Possible performance risks
            - Recommended improvements
            - How to measure or verify each hypothesis

            Do not claim that a performance issue is confirmed
            without sufficient evidence.
            """.formatted(module);

        return userPrompt(
            "Java performance analysis",
            instruction
        );
    }

    private GetPromptResult userPrompt(
            String description,
            String text
    ) {
        return GetPromptResult.builder(
            List.of(
                new PromptMessage(
                    Role.USER,
                    TextContent.builder(text).build()
                )
            )
        ).description(description).build();
    }
}