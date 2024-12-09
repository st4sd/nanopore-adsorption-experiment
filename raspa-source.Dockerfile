# syntax=docker/dockerfile:1
FROM registry.access.redhat.com/ubi9/ubi:9.0.0

# Define default parameters
ARG VERSION
WORKDIR /raspa/
ENV RASPA_DIR=/usr/local
ENV FORCEFIELD_DIR=/raspa/forcefield
ENV CFLAGS="-Ofast -march=x86-64 -mtune=generic"

# Install Python, GCC and build dependencies
RUN dnf -y install --disableplugin=subscription-manager automake diffutils flexiblas-netlib fftw-devel file gcc-c++ libtool make python3-pip python3-devel which && \
    alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    dnf --disableplugin=subscription-manager clean all && \
    pip install --no-cache-dir pipenv==2022.10.25 && \
    rm -rf /var/cache/dnf/*

# Download and compile RASPA source code
RUN curl https://codeload.github.com/iRASPA/RASPA2/tar.gz/v${VERSION} --output raspa.tar.gz && \
    tar zxfv raspa.tar.gz && \
    cd RASPA2-${VERSION} && \
    mkdir m4 && \
    aclocal && \
    autoreconf -i && \
    automake --add-missing && \
    autoconf && \
    ./configure --prefix=${RASPA_DIR} && \
    make -j4 && \
    make install && \
    cd .. && \
    rm -fr raspa.tar.gz RASPA2-${VERSION}

# Adding group permissions to ${RASPA_DIR}/share/raspa/
RUN chgrp -R 0 ${RASPA_DIR}/share/raspa/ && \
    chmod -R g+rwX ${RASPA_DIR}/share/raspa/

# Install Python dependencies
COPY Pipfile /raspa/
RUN pipenv install --skip-lock --system --verbose && \
    pipenv --clear

# Copy RASPA force fields
COPY forcefield ${FORCEFIELD_DIR}

# Copy Python scripts
COPY bin        /raspa/bin
