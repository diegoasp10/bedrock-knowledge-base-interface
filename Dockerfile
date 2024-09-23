FROM python:3.12-alpine

WORKDIR /app

# Instalar las dependencias necesarias
RUN apk update && apk add --no-cache \
    cmake \
    g++ \
    make \
    libgcc \
    libstdc++ \
    linux-headers \
    musl-dev \
    py3-pip \
    curl \
    bash \
    zlib-dev \
    bzip2-dev \
    boost-dev

# Copia la aplicación
COPY . /app

# Instalar las dependencias de Python
RUN pip3 install --no-cache-dir -r app/requirements.txt

# Exponer el puerto para Streamlit
EXPOSE 8501

# HEALTHCHECK para comprobar el estado de la aplicación
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Configurar la entrada para ejecutar Streamlit
ENTRYPOINT ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
