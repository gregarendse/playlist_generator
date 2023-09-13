FROM python:3

ENV directory=/workspace

WORKDIR ${directory}


# Install latest chrome dev package and fonts to support major charsets (Chinese, Japanese, Arabic, Hebrew, Thai and a few others)
# Note: this installs the necessary libs to make the bundled version of Chrome that Puppeteer
# installs, work.
RUN \
    set -x \
    &&  apt-get update \
    &&  apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    chromium \
    xvfb \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-thai-tlwg \
    fonts-khmeros \
    fonts-kacst \
    fonts-freefont-ttf libxss1 \
    &&  rm -rf /var/lib/apt/lists/*

RUN \
    set -x  \
    &&  groupadd -r playlister  \
    &&  useradd -rm -g playlister -G audio,video playlister \
    &&  chown playlister ${directory}

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

USER playlister


CMD [ "python", "-m" , "playlister" ]
