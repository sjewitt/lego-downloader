set +v
loop() {
	i=1

	#see https://www.cyberciti.biz/faq/bash-infinite-loop/
	while true
	do
		echo triggering plans retrieval [ctrl+c to end]...
		python3 legoFileStore.py
		echo done.
		sleep 1
	done
}
loop
 