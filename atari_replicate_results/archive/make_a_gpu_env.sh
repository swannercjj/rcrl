module load python/3.11 StdEnv/2023 gcc opencv/4.8.1 swig && \
	ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3` && \
	export ALL_PROXY=socks5h://localhost:8888
	#export ALL_PROXY="https://localhost:8888/"

mkdir -p /tmp/gwen/virtualenvs && \
	cd /tmp/gwen/virtualenvs && \
	echo "making venv" && \
	virtualenv pyenv && \
	source pyenv/bin/activate && \
	echo "activated..." && \
	pip install 'requests[socks]' --no-index && \
	pip install --no-cache-dir autorom gymnasium "gymnasium[classic-control,box2d,atari,other]" "numpy<2" "stable_baselines3==2.0.0a1" tqdm tyro torch tensorboard wandb --index-url https://pypi.org/simple && \
	AutoROM -y && \
	# https://stackoverflow.com/questions/78498481/userwarning-plan-failed-with-a-cudnnexception-cudnn-backend-execution-plan-des
	#pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
	echo "finished installing packages" && \
	pip list && \

	cd /tmp/gwen/ && \
	echo "zipping..." && \

	tar -czf atarigpuenv.tar.gz virtualenvs && \
	echo "moving..." && \
	mv atarigpuenv.tar.gz ~/projects/def-mbowling/gwynetha/ && \

	echo "cleaning up..." && \
	rm -fr /tmp/gwen

echo "done"

