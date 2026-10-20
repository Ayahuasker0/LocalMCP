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
You need to build Spring Boot MCP server 
```
cd mcp-servers/system-server
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
