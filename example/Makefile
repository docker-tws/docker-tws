# Deploy combined paper/live pod.
apply:
	kubectl apply -f tws-namespace.yml
	$(MAKE) k8s-conf
	kubectl apply -f tws-secrets.yml
	kubectl apply -f tws-combined.yml

# Deploy separate pods for paper / live.
apply-separate:
	kubectl apply -f tws-namespace.yml
	$(MAKE) k8s-conf
	kubectl apply -f tws-secrets.yml
	kubectl apply -f tws-paper.yml
	kubectl apply -f tws-live.yml

k8s-delete:
	kubectl delete --ignore-not-found=true -f tws-combined.yml
	kubectl delete --ignore-not-found=true -f tws-paper.yml
	kubectl delete --ignore-not-found=true -f tws-live.yml
	kubectl delete --ignore-not-found=true -f tws-secrets.yml
	kubectl delete --ignore-not-found=true -f tws-namespace.yml

# Expects jts.ini and tws.xml to be stored in conf/live/
k8s-conf:
	rm -rf conf/live.tmp
	cp -a conf/live conf/live.tmp
	gzip conf/live.tmp/tws.xml
	kubectl -n tws delete --ignore-not-found secret ibkr-conf 
	kubectl -n tws \
		create secret generic ibkr-conf \
		--save-config=false \
		--from-file=conf/live.tmp/ \
		--dry-run=true -o yaml | \
		kubectl create -f -
	rm -rf conf/live.tmp
