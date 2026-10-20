You need to build Spring Boot MCP server firstly:
```
cd mcp-servers/system-server
mvn clean package
```
Then 
```
cd ../..
python agent/llm_client.py
```
