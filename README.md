# Tokyo Land Price RAG

<img width="3024" height="1964" alt="screenshot" src="https://github.com/user-attachments/assets/24726433-0883-410c-aeb6-d9a7c86f1c94" />

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A Retrieval-Augmented Generation (RAG) application for exploring Tokyo land prices using an interactive map

## Demo

<p> <strong><a href="https://tokyolandpriceai.com" target="_blank">tokyolandpriceai.com</a></strong> </p>

### Example questions

- Which areas in Tokyo have the highest land prices?
- Where are good residential areas near Shibuya?

## Setup

### Prerequisites

- [Mapbox API key](https://www.mapbox.com)
- [Docker](https://www.docker.com)

1. Start Docker:

```bash
docker compose up -d
```

2. Set up Qdrant. Follow the guide [here](./scripts/README.md).

3. Set up Lambda. Follow the guide [here](./server/README.md).

4. Access http://localhost:5173/.

## Tech Stack

- Frontend: Vue
- Backend: AWS Lambda
- Hosting: Cloudflare, Fly.io
- Infrastructure: AWS SAM
- LLM: OpenAI API
- Vector Search DB: Qdrant
- Local Development: Docker, LocalStack
- Others: OpenStreetMap, Mapbox, Maplibre

## Contribution

- Bug fix PRs are always appreciated.
- UI changes or new features should not be submitted without prior discussion. Please open an issue first to propose and discuss them.

Thanks for your understanding and contributions.

## Credits

- Source: 国土数値情報 （地価公示データ）（国土交通省）https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2025.html

  The original data has been processed and transformed for visualization purposes.

## License

[MIT](./LICENSE)

Copyright (c) 2026-present, Akinori Hoshina
