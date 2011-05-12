dojo.provide("twdojo.data.TWDojoRestStore");

dojo.require("dojox.data.JsonRestStore");

dojo.declare("twdojo.data.TWDojoRestStore",
	[dojox.data.JsonRestStore],
	{
	    
	_processResults: function(results, deferred){
		// index the results
		var count = results.length;
		// if we don't know the length, and it is partial result, we will guess that it is twice as big, that will work for most widgets
		return {totalCount:results.totalCount || (deferred.request.count == count ? count * 2 : count), items: results.items};
	},
    onSet: function(){
        if (this.autoSave) this.save();
        }
	}
);