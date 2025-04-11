# Shikinha

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)

## What is Shikinha?

Shikinha is a simple Discord music bot, built using Python.
  
The default prefix for the bot is ```;```

## Setting up...

First, you'll need a Discord API token, which you can get from the [Discord developer portal](https://discord.com/developers/applications). Create a new application and generate a token. After obtaining the token, paste it into the ```disc_token``` variable in the ```config.toml``` file.

With that done, you can set up the bot in two ways: Local or via Docker. Choose the method that suits you best.

### Method 1: Local Setup
1. First, make sure you have Python 3.11+ installed. You can check this by running:
   
    ```
    python3 --version
    ```
2. Install the required dependencies listed in the requirements.txt file by running:
   
    ```
    pip install -r requirements.txt
    ```
3. After the dependencies are installed, ensure that you have the necessary ```ffmpeg``` package is installed on your system, as it's required for audio processing. You can install it by running:

    #### For Linux:
      ```
      sudo apt-get install ffmpeg
      ```
    #### For macOS (using Homebrew):
      ```
      brew install ffmpeg
      ```

    For Windows, follow the instructions [here](https://ffmpeg.org/download.html).

4. Once everything is set up, run the bot with:
    ```
    python3 shikinha.py
    ```

### Method 2: Docker Setup (Recommended)
  1. Ensure that Docker is installed on your system. If not, follow the installation instructions on the [official Docker website](https://www.docker.com).
  2. Build and run the Docker container with the following commands:
     
      ```
      docker build -t shikinha .
      docker run -p 443:443 shikinha
      ```
      This will build the Docker image, install all necessary dependencies (including ```ffmpeg```), and run the bot.
      
## Commands

### Music:
  * ```play [Music/URL]```
    * Plays a song by searching YouTube for the provided query or from a direct URL (YouTube link).
  * ```skip```
    * Skips the currently playing song.
  * ```pause```
    * Pauses the currently playing song.
  * ```resume```
    * Resumes the currently paused song.
  * ```queue```
  	* Displays the current music queue.
  * ```leave```
  	* Makes Shikinha disconnect from your voice channel.

### Miscellaneous:
* ```help```
  * Displays a help message.
* ```ping```
  * Shows the bot's latency.
* ```mp3 [URL]```
  * Downloads and sends an MP3 version of the provided audio/video URL.
  * ⚠️ This command will not work if the final audio file is larger than 8 MB, due to Discord's file size limit for uploads. The file is encoded at 128kbps to help keep it within this limit.
* ```cat```
  * Shows a picture of a random cat.
* ```dog```
  * Shows a picture of a random dog.
* ```e621 [tags]```(NSFW)
  * Searches for a random post on E621 with the provided tags.
* ```rule34 [tags]``` (NSFW)
  * Searches for a random post on Rule34 with the provided tags.
