FROM registry.access.redhat.com/ubi9/ubi:9.0.0

# Define default parameters
WORKDIR /raspa/
ENV FORCEFIELD_DIR=/raspa/forcefield
ENV RASPA_DIR=/usr/local/lib64/python3.9/site-packages/RASPA2

# Install Python and GCC
RUN dnf -y install --disableplugin=subscription-manager gcc gcc-c++ python3-pip python3-devel && \
    alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    dnf --disableplugin=subscription-manager clean all && \
    pip install --no-cache-dir pipenv==2022.9.24 && \
    rm -rf /var/cache/dnf/*

# Install Python dependencies
COPY Pipfile /raspa/
RUN pipenv install --dev --skip-lock --system --verbose && \
    pipenv --clear

# Copy RASPA force fields
COPY forcefield ${FORCEFIELD_DIR}

# Copy Python scripts
COPY bin        /raspa/bin
