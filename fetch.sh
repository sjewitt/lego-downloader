set +v
loop() {
	i=1

	#see https://www.cyberciti.biz/faq/bash-infinite-loop/
	while true
	do
		echo triggering plans retrieval [ctrl+c to end]...
		python3 fetcher.py -d 192.168.1.115
		echo done.
		sleep 1
	done
}
loop
 
