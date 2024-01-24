# Use latest Ubuntu image
FROM ubuntu:latest

# Install Python 3.10
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-distutils python3.10-venv

# Install pip
RUN apt-get install -y python3-pip

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    node --version && \
    npm --version

# 複製 npm 項目到容器中（包括 package.json 和其他必要檔案）
COPY . /app

# 設定工作目錄
WORKDIR /app

# # Install pip dependencies
RUN pip3 install -r pip_requirements.txt

# Install node dependencies
RUN npm install

# Build container
RUN npm run build

# 容器啟動時執行的命令
CMD ["npm", "run", "start"]
