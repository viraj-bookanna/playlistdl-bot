# playlistdl-bot
.m3u8 playlist downloader bot with telethon,ffmpeg

## Docker Setup Guide

1. **Clone the repository:**
    ```bash
    git clone https://github.com/viraj-bookanna/playlistdl-bot
    cd playlistdl-bot
    ```

2. **Build the Docker image:**
    ```bash
    docker build -t playlistdl-bot .
    ```

3. **Create and edit the environment file:**
    ```bash
    cp .env.sample .env
    nano .env
    ```
    Update the environment variables in `.env` as needed.

4. **Run the container:**
    ```bash
    docker run -d --name playlistdl-bot \
      --env-file .env \
      playlistdl-bot
    ```
