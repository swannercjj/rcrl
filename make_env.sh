module load python/3.11.5 StdEnv/2023 swig && \
	ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3` && \
	export ALL_PROXY=socks5h://localhost:8888

mkdir -p /tmp/jiajing/virtualenvs && \ # can change this directory name if you want, but will be deleted in the end
	cd /tmp/jiajing/virtualenvs && \
	echo "making venv" && \
	virtualenv --no-download pyenv && \
	source pyenv/bin/activate && \
	echo "activated..." && \
	pip install requests[socks] --no-index && \
	echo "has socks..." && \
	pip install --no-cache-dir "gymnasium[classic-control]" "gymnasium[box2d]" numpy "stable_baselines3==2.0.0a1" tqdm tyro torch tensorboard wandb --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cpu && \
	echo "finished installing packages" && \
	cd /tmp/jiajing/ && \
	echo "zipping..." && \

	tar -czf pyenv.tar.gz virtualenvs && \
	echo "moving..." && \
	mv pyenv.tar.gz ~/projects/def-mbowling/jiajing8/ && \ # make sure to change to your directory

	echo "cleaning up..." && \
	rm -fr /tmp/jiajing

echo "done"
