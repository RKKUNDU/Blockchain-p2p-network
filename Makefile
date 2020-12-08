clean:
	$(RM) ./peer_output/peer_output_* ./peer_output/adversary_output_* seed_output_*
	$(RM) -r __pycache__

hard_clean:
	$(RM) graph_data/* 
	$(RM) -r peer_log_*/
