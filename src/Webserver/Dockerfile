FROM php:7.4-apache
RUN a2enmod rewrite && a2enmod ssl && a2enmod socache_shmcb
RUN sed -i '/SSLCertificateFile.*snakeoil\.pem/c\SSLCertificateFile \/etc\/ssl\/certs\/webserver.info.crt' /etc/apache2/sites-available/default-ssl.conf && sed -i '/SSLCertificateKeyFile.*snakeoil\.key/cSSLCertificateKeyFile /etc/ssl/private/webserver.info.key\' /etc/apache2/sites-available/default-ssl.conf
RUN a2ensite default-ssl
RUN apt-get update && apt-get upgrade -y