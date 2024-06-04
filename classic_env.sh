# Run this on interactive mode
module load StdEnv/2023
module load python/3.10.13

ssh -q -N -T -f -D 8888 `echo $SSH_CONNECTION | cut -d " " -f 3`
export ALL_PROXY=socks5h://localhost:8888
mkdir -p /tmp/gwen/virtualenvs
cd /tmp/gwen/virtualenvs 
virtualenv classicenv
. classicenv/bin/activate
pip install requests[socks] --no-index
# put in directory to requirements file
pip install -r /home/gwynetha/projects/def-mbowling/gwynetha/rcrl/control_req.txt --no-index

echo "installed packages:"
pip list
cd /tmp/gwen
tar -czf classicenv.tar.gz virtualenvs
cp classicenv.tar.gz ~/projects/def-mbowling/gwynetha/
rm -fr /tmp/gwen
echo "Done."