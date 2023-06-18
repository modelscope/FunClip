#!/usr/bin/env bash

scriptVersion="0.0.1"
scriptDate="20230615"

clear


# Set color
RED="\033[31;1m"
GREEN="\033[32;1m"
YELLOW="\033[33;1m"
BLUE="\033[34;1m"
PURPLE="\033[35;1m"
CYAN="\033[36;1m"
PLAIN="\033[0m"

# Info messages
FAIL="${RED}[FAIL]${PLAIN}"
DONE="${GREEN}[DONE]${PLAIN}"
ERROR="${RED}[ERROR]${PLAIN}"
WARNING="${YELLOW}[WARNING]${PLAIN}"
CANCEL="${CYAN}[CANCEL]${PLAIN}"

# Font Format
BOLD="\033[1m"
UNDERLINE="\033[4m"

# Current folder
cur_dir=`pwd`

# Make sure root user
rootNess(){
    echo "${BOLD}[0/10]"
    echo "Check root ness"

    if [[ $EUID -ne 0 ]]; then
        echo -e "${WARNING} MUST RUN AS ${RED}ROOT${PLAIN} USER!"
        exit 1
    fi

    cd ${cur_dir}

    clear
}

# Install docker
installDocker(){
    echo "${BOLD}[1/10]"

    if [ $DOCKERINFOLEN -gt 30 ]; then
        echo "Docker has installed."
    else
        lowercase_osid=$(echo $OSID | tr '[A-Z]' '[a-z]')
        echo "Start install docker for $lowercase_osid"
        DOCKER_INSTALL_CMD="curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun"
        DOCKER_INSTALL_RUN_CMD=""

        case "$lowercase_osid" in
            ubuntu)
                DOCKER_INSTALL_CMD="curl -fsSL https://test.docker.com -o test-docker.sh"
                DOCKER_INSTALL_RUN_CMD="sudo sh test-docker.sh"
                ;;
            centos)
                DOCKER_INSTALL_CMD="curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun"
                ;;
            debian)
                DOCKER_INSTALL_CMD="curl -fsSL https://get.docker.com -o get-docker.sh"
                DOCKER_INSTALL_RUN_CMD="sudo sh get-docker.sh"
                ;;
            *)
                echo "$lowercase_osid is not supported."
                ;;
        esac

        echo "get docker installer: $DOCKER_INSTALL_CMD"
        echo "get docker run: $DOCKER_INSTALL_RUN_CMD"

        $DOCKER_INSTALL_CMD
        if [ ! -z "$DOCKER_INSTALL_RUN_CMD" ]; then
            $DOCKER_INSTALL_RUN_CMD
        fi

        DOCKERINFO=$(sudo docker info | wc -l)
        DOCKERINFOLEN=$(expr $DOCKERINFO)
        if [ $DOCKERINFOLEN -gt 30 ]; then
            echo "Docker install success, start docker server."
            sudo systemctl start docker
        else
            echo -e "Docker install failed!"
            exit 1
        fi
    fi

    sleep 3
    clear
}

# Download docker image
downloadDockerImage(){
    echo "${BOLD}[2/10]"
    echo "Pull docker image ..."

    sudo docker pull funasr/funasr:0.5.4-torch1.11.0-cuda113-py3.7-ubuntu20.04-modelscope1.5.0

    sleep 3
    clear
}

# Set model path for FunASR server
setupAsrModelId(){
    echo "${BOLD}[3/10]"

    default_model_id="speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"

    echo "${GREEN}Please input model path in local host for FunASR server:${PLAIN}"
    echo "default model path: ${PARAMS_LOCAL_MODEL_ID}"
    echo "will download model if use this default model."
    echo "-> "
    read -p "read model path: " PARAMS_LOCAL_MODEL_ID

    if [ -z "$PARAMS_LOCAL_MODEL_ID" ]; then
        PARAMS_LOCAL_MODEL_ID=${cur_dir}/${default_model_id}
        echo "local model_id ${PARAMS_LOCAL_MODEL_ID}"
        if [ ! -e $PARAMS_LOCAL_MODEL_ID ]; then
            echo "use default model_id ${default_model_id}, downloading ..."
            wget --no-check-certificate https://swap.oss-cn-hangzhou.aliyuncs.com/shichen.fsc/MaaS/asr/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch.tar.gz
            echo "decompressing ..."
            tar -zxf ${default_model_id}.tar.gz
        else
            echo "${PARAMS_LOCAL_MODEL_ID} is existing."
        fi
    fi

    PARAMS_LOCAL_MODEL_DIR=$(dirname "$PARAMS_LOCAL_MODEL_ID")
    MODEL_ID=$(basename "$PARAMS_LOCAL_MODEL_ID")
    PARAMS_DOCKER_MODEL_DIR="/tests"
    PARAMS_DOCKER_MODEL_ID=${PARAMS_DOCKER_MODEL_DIR}/${MODEL_ID}
    echo
}

# Set server exec for FunASR
setupServerExec(){
    echo "${BOLD}[4/10]"

    echo "${GREEN}Please input exec path in local host for FunASR server:${PLAIN}"
    echo "will use default exec in docker(${PARAMS_DOCKER_EXEC}) if donnot set this parameter."
    echo "-> "
    read -p "read exec path in local host: " PARAMS_LOCAL_EXEC

    if [ -z $PARAMS_LOCAL_EXEC ]; then
        PARAMS_LOCAL_EXEC_DIR=""
        PARAMS_LOCAL_EXEC=""
    else
        if [ ! -f $PARAMS_LOCAL_EXEC ]; then
            PARAMS_LOCAL_EXEC_DIR=""
            PARAMS_LOCAL_EXEC=""
        else
            PARAMS_LOCAL_EXEC_DIR=$(dirname "$PARAMS_LOCAL_EXEC")
            EXEC_ID=$(basename "$PARAMS_LOCAL_EXEC")
            PARAMS_DOCKER_EXEC_DIR="/tests"
            PARAMS_DOCKER_EXEC=${PARAMS_DOCKER_EXEC_DIR}/${EXEC_ID}
        fi
    fi
    echo
}

# Configure FunASR server host port setting
setupHostPort(){
    echo "${BOLD}[5/10]"

    while true
    do
    echo "${GREEN}Please input port for docker mapped [1-65535]:${PLAIN}"
    echo "default: 8889"
    echo "-> "
    read -p "read host port: " PARAMS_HOST_PORT

    if [ -z "$PARAMS_HOST_PORT" ]; then
        PARAMS_HOST_PORT="8889"
    fi
    expr ${PARAMS_HOST_PORT} + 0
    if [ $? -eq 0 ]; then
        if [ ${PARAMS_HOST_PORT} -ge 1 ] && [ ${PARAMS_HOST_PORT} -le 65535 ]; then
            break
        else
            echo "Input error, please input correct number!"
        fi
    else
        echo "Input error, please input correct number!"
    fi
    done
    echo
}

# Configure FunASR server docker port setting
setupDockerPort(){
    echo "${BOLD}[6/10]"

    while true
    do
    echo "${GREEN}Please input port for docker mapped [1-65535]:${PLAIN}"
    echo "default: 8889, the opened port of current host is ${PARAMS_HOST_PORT}"
    echo "-> "
    read -p "read docker port: " PARAMS_DOCKER_PORT

    if [ -z "$PARAMS_DOCKER_PORT" ]; then
        PARAMS_DOCKER_PORT="8889"
    fi
    expr ${PARAMS_DOCKER_PORT} + 0
    if [ $? -eq 0 ]; then
        if [ ${PARAMS_DOCKER_PORT} -ge 1 ] && [ ${PARAMS_DOCKER_PORT} -le 65535 ]; then
            break
        else
            echo "Input error, please input correct number!"
        fi
    else
        echo "Input error, please input correct number!"
    fi
    done
    echo
}

setupDecoderThreadNum(){
    echo "${BOLD}[7/10]"

    while true
    do
    echo "${GREEN}Please input thread number for FunASR decoder:${PLAIN}"
    echo "default: 32"
    echo "-> "
    read -p "read decoder thread number: " PARAMS_DECODER_THREAD_NUM

    if [ -z "$PARAMS_DECODER_THREAD_NUM" ]; then
        PARAMS_DECODER_THREAD_NUM="32"
    fi
    expr ${PARAMS_DECODER_THREAD_NUM} + 0
    if [ $? -eq 0 ]; then
        if [ ${PARAMS_DECODER_THREAD_NUM} -ge 1 ] && [ ${PARAMS_DECODER_THREAD_NUM} -le 65535 ]; then
            break
        else
            echo "Input error, please input correct number!"
        fi
    else
        echo "Input error, please input correct number!"
    fi
    done
    echo
}


setupIoThreadNum(){
    echo "${BOLD}[8/10]"

    while true
    do
    echo "${GREEN}Please input thread number for server IO:${PLAIN}"
    echo "default: 8"
    echo "-> "
    read -p "read io thread number: " PARAMS_IO_THREAD_NUM

    if [ -z "$PARAMS_IO_THREAD_NUM" ]; then
        PARAMS_IO_THREAD_NUM="8"
    fi
    expr ${PARAMS_IO_THREAD_NUM} + 0
    if [ $? -eq 0 ]; then
        if [ ${PARAMS_IO_THREAD_NUM} -ge 1 ] && [ ${PARAMS_IO_THREAD_NUM} -le 65535 ]; then
            break
        else
            echo "Input error, please input correct number!"
        fi
    else
        echo "Input error, please input correct number!"
    fi
    done
    echo
}

showAllParams(){
    echo "${BOLD}[9/10]"
    echo "Show parameters of FunASR server setting and confirm to run ..."
    echo
    echo "The path to the local model directory for the load:${YELLOW} ${PARAMS_LOCAL_MODEL_ID} ${PLAIN}"
    echo "The model directory corresponds to the directory in Docker:${YELLOW} ${PARAMS_DOCKER_MODEL_ID} ${PLAIN}"

    echo
    echo "The local path of the FunASR service executor:${YELLOW} ${PARAMS_LOCAL_EXEC} ${PLAIN}"
    echo "The path in the docker of the FunASR service executor:${YELLOW} ${PARAMS_DOCKER_EXEC} ${PLAIN}"

    echo
    echo "Set the host port used for use by the FunASR service:${YELLOW} ${PARAMS_HOST_PORT} ${PLAIN}"
    echo "Set the docker port used by the FunASR service:${YELLOW} ${PARAMS_DOCKER_PORT} ${PLAIN}"

    echo
    echo "Set the number of threads used for decoding the FunASR service:${YELLOW} ${PARAMS_DECODER_THREAD_NUM} ${PLAIN}"
    echo "Set the number of threads used for IO the FunASR service:${YELLOW} ${PARAMS_IO_THREAD_NUM} ${PLAIN}"   

    echo
    while true
    do
    PARAMS_CONFIRM="y"
    echo "${GREEN}Please input [y/n] to confirm the parameters.${PLAIN}"
    echo "[y] Verify that these parameters are correct and that the service will run."
    echo "[n] The parameters set are incorrect, it will be rolled out, please rerun."
    echo "-> "
    read -p "read confirmation[y/n] " PARAMS_CONFIRM

    if [ -z "$PARAMS_CONFIRM" ]; then
        PARAMS_CONFIRM="y"
    fi
    YES="y"
    NO="n"
    echo "confirm: $PARAMS_CONFIRM"
    if [ "$PARAMS_CONFIRM" = "$YES" ]; then
        echo "Will run FunASR server later ..."
        break
    elif [ "$PARAMS_CONFIRM" = "$NO" ]; then
        echo "The parameters set are incorrect, please rerun ..."
        exit 1
    else
        echo "again ..."
    fi
    done
    sleep 3
    clear
}

dockerRun(){
    echo "${BOLD}[10/10]" 
    echo "Construct command and run docker ..."

    RUN_CMD="sudo docker run"
    PORT_MAP=" -p ${PARAMS_HOST_PORT}:${PARAMS_DOCKER_PORT}"
    DIR_PARAMS=" -it --privileged=true"
    DIR_MAP_PARAMS=""
    if [ ! -z ${PARAMS_LOCAL_MODEL_DIR} ]; then
        DIR_MAP_PARAMS="${DIR_PARAMS} -v ${PARAMS_LOCAL_MODEL_DIR}:${PARAMS_DOCKER_MODEL_DIR}"
    fi
    if [ ! -z ${PARAMS_LOCAL_EXEC_DIR} ]; then
        if [ -z ${DIR_MAP_PARAMS} ]; then
            DIR_MAP_PARAMS="${DIR_PARAMS} -v ${PARAMS_LOCAL_EXEC_DIR}:${PARAMS_DOCKER_EXEC_DIR}"
        else
            DIR_MAP_PARAMS="${DIR_MAP_PARAMS} -v ${PARAMS_LOCAL_EXEC_DIR}:${PARAMS_DOCKER_EXEC_DIR}"
        fi
    fi

    EXEC_PARAMS="\\\"exec\\\":\\\"${PARAMS_DOCKER_EXEC}\\\""
    MODEL_PARAMS="\\\"--model-dir\\\":\\\"${PARAMS_DOCKER_MODEL_ID}\\\""
    DECODER_PARAMS="\\\"--decoder_thread_num\\\":\\\"${PARAMS_DECODER_THREAD_NUM}\\\""
    IO_PARAMS="\\\"--io_thread_num\\\":\\\"${PARAMS_IO_THREAD_NUM}\\\""
    PORT_PARAMS="\\\"--port\\\":\\\"${PARAMS_DOCKER_PORT}\\\""

    ENV_PARAMS=" --env DAEMON_SERVER_CONFIG={\\\"server\\\":[{${EXEC_PARAMS},${MODEL_PARAMS},${DECODER_PARAMS},${IO_PARAMS},${PORT_PARAMS}}]}"

    RUN_CMD="${RUN_CMD}${PORT_MAP}${DIR_MAP_PARAMS}${ENV_PARAMS}"
    RUN_CMD="${RUN_CMD} funasr/funasr:0.5.4-torch1.11.0-cuda113-py3.7-ubuntu20.04-modelscope1.5.0"

    sleep 3
    ${RUN_CMD}
    clear
}


# Display Help info
displayHelp(){
    echo -e "${UNDERLINE}Usage${PLAIN}:"
    echo -e "  $0 [OPTIONAL FLAGS]"
    echo
    echo -e "funasr.sh - a Bash script to install&run FunASR docker."
    echo
    echo -e "${UNDERLINE}Options${PLAIN}:"
    echo -e "   ${BOLD}-i, --install${PLAIN}      Install FunASR docker."
    echo -e "   ${BOLD}-v, --version${PLAIN}      Display current script version."
    echo -e "   ${BOLD}-h, --help${PLAIN}         Display this help."
    echo
    echo -e "${UNDERLINE}funasr.sh${PLAIN} - Version ${scriptVersion} "
    echo -e "Modify Date ${scriptDate}"
}

# Install main function
installFunasrDocker(){
    installDocker
    downloadDockerImage
    setupAsrModelId
    setupServerExec
    setupHostPort
    setupDockerPort
    setupDecoderThreadNum
    setupIoThreadNum
}

# OS
OSID=$(grep ^ID= /etc/os-release | cut -d= -f2)
OSVER=$(lsb_release -cs)
OSNUM=$(grep -oE  "[0-9.]+" /etc/issue)
DOCKERINFO=$(sudo docker info | wc -l)
DOCKERINFOLEN=$(expr $DOCKERINFO)

# PARAMS
PARAMS_LOCAL_EXEC=""
PARAMS_LOCAL_EXEC_DIR=""
PARAMS_DOCKER_EXEC="/mnt/FunASR/funasr/runtime/websocket/build/bin/websocketmain"
PARAMS_DOCKER_EXEC_DIR=""
PARAMS_LOCAL_MODEL_DIR=""
PARAMS_LOCAL_MODEL_ID=""
PARAMS_DOCKER_MODEL_DIR=""
PARAMS_DOCKER_MODEL_ID=""
PARAMS_HOST_PORT="8889"
PARAMS_DOCKER_PORT="8889"
PARAMS_DECODER_THREAD_NUM="32"
PARAMS_IO_THREAD_NUM="8"


echo -e "#############################################################"
echo -e "#       ${RED}OS${PLAIN}: $OSID $OSNUM $OSVER "
echo -e "#   ${RED}Kernel${PLAIN}: $(uname -m) Linux $(uname -r)"
echo -e "#      ${RED}CPU${PLAIN}: $(grep 'model name' /proc/cpuinfo | uniq | awk -F : '{print $2}' | sed 's/^[ \t]*//g' | sed 's/ \+/ /g') "
echo -e "#      ${RED}RAM${PLAIN}: $(cat /proc/meminfo | grep 'MemTotal' | awk -F : '{print $2}' | sed 's/^[ \t]*//g') "
echo -e "#############################################################"
echo

# Initialization step
case "$1" in
    install|-i|--install)
        rootNess
        installFunasrDocker
        showAllParams
        dockerRun
        ;;
    *)
        clear
        displayHelp
        exit 0
        ;;
esac
