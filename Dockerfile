FROM golang:1.24

WORKDIR /app

COPY src .

RUN apt update
# Install python module
RUN apt install -y python3-pip
RUN pip install python-dotenv jinja2 rich ping3 --break-system-packages
# Install tools
RUN go install github.com/d3mondev/puredns/v2@latest
RUN cd install/massdns; make; make install

RUN go install github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN go install github.com/tomnomnom/waybackurls@latest
RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

RUN go install github.com/incogbyte/shosubgo@latest


ENTRYPOINT ["python3","main.py"]
