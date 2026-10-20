package com.example.mcp.tools;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

@Component
public class CalculatorTools {

    @Tool(
            name = "calculate",
            description = "Performs arithmetic operations on two numbers"
    )
    public double calculate(
            @ToolParam(description = "First number") double a,
            @ToolParam(description = "Second number") double b,
            @ToolParam(description = "Operation: add, subtract, multiply, divide")
            String operation
    ) {
        return switch (operation.toLowerCase()) {
            case "add" -> a + b;
            case "subtract" -> a - b;
            case "multiply" -> a * b;
            case "divide" -> {
                if (b == 0) {
                    throw new IllegalArgumentException(
                            "Division by zero is not allowed"
                    );
                }
                yield a / b;
            }
            default -> throw new IllegalArgumentException(
                    "Unsupported operation: " + operation
            );
        };
    }
}