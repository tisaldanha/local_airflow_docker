FROM apache/airflow:2.4.1
USER root

# Install MSSQL Drivers
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Common libs used on Airflow development
USER airflow
RUN pip install --no-cache-dir statsd==3.3.0
RUN pip install --no-cache-dir oauthlib==3.2.1
RUN pip install --no-cache-dir pandas==1.3.5
RUN pip install --no-cache-dir pyarrow==6.0.1
RUN pip install --no-cache-dir google-cloud-bigquery==2.34.4
RUN pip install --no-cache-dir apache-airflow-providers-tableau==3.0.1
RUN pip install --no-cache-dir apache-airflow-providers-amazon==6.0.0
RUN pip install --no-cache-dir apache-airflow-providers-common-sql==1.2.0
RUN pip install --no-cache-dir apache-airflow-providers-ftp==3.1.0
RUN pip install --no-cache-dir apache-airflow-providers-http==4.0.0
RUN pip install --no-cache-dir apache-airflow-providers-imap==3.0.0
RUN pip install --no-cache-dir apache-airflow-providers-microsoft-mssql==3.2.1
RUN pip install --no-cache-dir apache-airflow-providers-odbc==3.1.2
RUN pip install --no-cache-dir apache-airflow-providers-slack==5.1.0
RUN pip install --no-cache-dir apache-airflow-providers-sqlite==3.2.1
RUN pip install --no-cache-dir apache-airflow-providers-tableau==3.0.1
