module load python/3.11.5 StdEnv/2023 swig && \
	ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3` && \
	export ALL_PROXY=socks5h://localhost:8888

mkdir -p /tmp/gwen/virtualenvs && \ 
	cd /tmp/gwen/virtualenvs && \
	echo "making venv" && \
	virtualenv --no-download pyenv && \
	source pyenv/bin/activate && \
	echo "activated..." && \
	pip install requests[socks] --no-index && \
	echo "has socks..." && \
	pip install --no-cache-dir "gymnasium[atari,accept-rom-license]"
	pip install --no-cache-dir "gymnasium[classic-control]" "gymnasium[box2d]" numpy "stable_baselines3==2.0.0a1" tqdm tyro torch tensorboard wandb --index-url https://pypi.org/simple --extra-index-url https://download.pytorch.org/whl/cpu && \
	echo "finished installing packages" && \
	cd /tmp/gwen/ && \
	echo "zipping..." && \

	tar -czf atarienv.tar.gz virtualenvs && \
	echo "moving..." && \
	mv atarienv.tar.gz ~/projects/def-mbowling/gwynetha/ && \ 

	echo "cleaning up..." && \
	rm -fr /tmp/gwen

echo "done"

# added "gymnasium[atariaccept-rom-license]"