package com.example.mcp.tools;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.revwalk.RevCommit;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

@Component
public class GitTools {
    private final int COMMIT_NUMBER_LIMIT = 30;

    private static final String REPO_PATH =
            System.getProperty("user.dir");

    @Tool(
            name = "git_status",
            description = "Returns the current Git repository status"
    )
    public String getStatus() throws Exception {

        try (Git git = Git.open(new File(REPO_PATH))) {
            return git.status().call().toString();
        }
    }

    @Tool(
            name = "git_branch",
            description = "Returns the current Git branch"
    )
    public String getBranch() throws Exception {

        try (Git git = Git.open(new File(REPO_PATH))) {
            return git.getRepository().getBranch();
        }
    }

    @Tool(
            name = "git_recent_commits",
            description = "Returns recent Git commits"
    )
    public List<String> getRecentCommits(
            @ToolParam(description = "Number of commits to retrieve")
            int limit
    ) throws Exception {

        if (limit < 1 || limit > COMMIT_NUMBER_LIMIT) {
            throw new IllegalArgumentException(
                    "Limit must be between 1 and 20"
            );
        }

        List<String> commits = new ArrayList<>();

        try (Git git = Git.open(new File(REPO_PATH))) {

            Iterable<RevCommit> history = git.log()
                    .setMaxCount(limit)
                    .call();

            for (RevCommit commit : history) {
                commits.add(
                        commit.getName() + " - " +
                                commit.getShortMessage()
                );
            }
        }

        return commits;
    }
}