Boilerplate for different aspects of full stack dev environment
- [Back-End](#back-kend)
- [Front-End](#front-end)
- [Database](#database)
- [CI / CD](#ci/cd)
- [Automation](#automation)




---

# Back-End

---


<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/php/php-original.svg"  width="15%" heigh="15%" align="center">
</p>

[Vanilla](https://www.php.net/docs.php)
- Development 7.4/8.4 base

[Symfony](https://symfony.com/doc/current/index.html)
- Web App / REST API base
- Custom functions for debugging, logs and maintenance

[Laravel](https://laravel.com/docs/12.x/installation)
- Web App base with Full-Stack [nginx,postgres,php,workspace]

[Wordpress](https://wordpress.org/documentation/)
- Base WP Blog with DB

[Vite + ReactJS](https://github.com/vitejs/vite/tree/main/packages/create-vite)
- React Web App base with Full-Stack dev:
	- [nginx,mariadb,php,redis,mailhog,phpmyadmin]
 	- [npm,composer,artisan]
  	- [laravel-cron,laravel-queue,laravel-migrate-seed]

-----

<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/python/python-original.svg" width="15%" heigh="15%" align="center">
</p>

[Vanilla](https://docs.python.org/3.12/py-modindex.html)
- Development 3.6 [Alpine: virtual-env & postgres]

[Django](https://docs.djangoproject.com/en/5.2/)
- Development 3.6 [Alpine: Postgres & django plugins]

[Flask](https://pypi.org/project/Flask/)
- Development 3.6 [Alpine: virtual-env & Postgres & Flask]




---

# Front-End

---


<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/javascript/javascript-plain.svg" width="15%" heigh="15%" align="center">
</p>

##### Coming soon
- Typescript
- VueJS
- ReactJS
- D3.js
- TreeJS

---


<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/html5/html5-plain.svg" width="15%" heigh="15%" align="center">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/css3/css3-plain.svg" width="15%" heigh="15%" align="center">
</p>

HTML boilerplate
- Html base tags with basic CSS

##### Coming soon
CSS boilerplate





---

# Database

---


<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mysql/mysql-plain-wordmark.svg" width="15%" heigh="15%" align="center" >
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/postgresql/postgresql-plain-wordmark.svg" width="15%" heigh="15%" align="center" >
</p>

[MariaDB](https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/installing-mariadb/binary-packages/automated-mariadb-deployment-and-administration/docker-and-mariadb)
- Build image with entrypoint + healthcheck

[PostGreSQL](https://docs.docker.com/reference/samples/postgres/)
- Build image with db init script

---

<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/mongodb/mongodb-plain-wordmark.svg"  width="15%" heigh="15%" align="center" >
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/redis/redis-plain-wordmark.svg" width="15%" heigh="15%" align="center" >
	<img src="https://github.com/user-attachments/assets/93862496-65c4-40d5-8f04-f81df9d03458" alt="InfluxDB logo" width="15%" align="center" >
</p>

[MongoDB](https://www.mongodb.com/docs/)
- Build base image with Mongo-Express container

[Redis](https://redis.io/docs/latest/operate/oss_and_stack/management/config/)
- Build base image container with config

[InfluxDB](https://docs.influxdata.com/)
- Build base image container with config



---

# CI/CD

---


### Continuous Integration Tools

<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/jenkins/jenkins-original.svg" width="15%" heigh="15%" align="center" >
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/gitlab/gitlab-original-wordmark.svg" width="15%" heigh="15%" align="center" >
</p>

[Jenkins](https://www.jenkins.io/doc/book/)
- Base for App testing

[Gitlab CE](https://docs.gitlab.com/)
- Base for git repos, issue tracking, CI/CD, Wiki, and more.




---

# Automation

---

<p align="left">
	<img src="https://cdn.jsdelivr.net/gh/devicons/devicon@latest/icons/ansible/ansible-original-wordmark.svg" width="15%" heigh="15%" align="center">
</p>

[Ansible](https://docs.ansible.com/ansible/latest/collections/community/docker/index.html)
- Base for agentless workflow automation + playbook yaml
