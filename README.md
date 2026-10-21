You need to install java 21
```
sudo apt install openjdk-21-jdk
```
and ollama qwen:8b (you can run another amount of parameters depend on hardware)
```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:8b
ollama run qwen3:8b
```
You need to build Spring Boot MCP servers
```
cd mcp-servers/system-server
mvn clean package
```
```
cd mcp-servers/git-server

mvn clean package
```
```
cd mcp-servers/project-server

mvn clean package
```
And install python requirements
```
pip install -r agent/requirements.txt
```
Then 
```
cd ../..
python agent/agent_loop.py
```
<li></li>
<li></li>
<li></li>

Important: Repository location
For this first implementation, JGit opens the repository at the Java process's working directory:
```
System.getProperty("user.dir")
```
That means the Git MCP server must be launched with the repository root as its working directory.

We'll explicitly configure this in the Python client.

Later, we'll improve the design by using a configurable repository path.

<li></li>
<li></li>
<li></li>

Build the Git MCP server
```
cd mcp-servers/git-server
mvn clean package
```
