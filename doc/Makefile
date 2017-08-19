doc:
	@epydoc -v --output=Documentation ../nvmf/*py ../*py ../utils/*py
	@make -C sequence-diag/

clean:
	@make -C sequence-diag/ clean
	@rm -fr Documentation 
