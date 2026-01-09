# coact

Użyte modele działały z Ollama, której obraz można łatwo pobrać i uruchomić w Docker:

```commandline
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

Po uruchomieniu konteneru Ollama można wprowadzić komendę, która pobierze porządany model LLM (np. llama3.1:8b):

```
docker exec -it ollama ollama pull llama3.1:8b
```

