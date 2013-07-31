var mapRename = function(){

	if(! this.sex.match(/persons/i)){
		return;
	} // will only emit for persons to prevent double counting 
	//(alternatively I could divide by 2 in the reduce function 
	// if i can trust the data

	var superRegion = this.super_region;
	var region;
	if(superRegion.match(/(australasia|oceania|polynesia|zealand|pacific)/i)){
		region = 'Oceania';
	}else if(superRegion.match(/europe/i)){
		region = 'Europe';
	}else if(superRegion.match(/asia/i)){
		region = 'Asia';
	}else if(superRegion.match(/africa/i)){
		region = 'Africa';
	}else if(superRegion.match(/america/i)){
		region = 'America';
	}
	//}else if(superRegion.match(/north.*america/i)){
		//region = 'North America';
	//}else if(superRegion.match(/south.*america/i)){
		//region = 'South America';
	//}
	
	var key = region + '_' + this.year;

	var value ={
		//region: region,
		//year: this.year,
		number: this.number
	}

	emit(key, value);
};

var reduceSumRegion = function(key, values){
	var fields = key.split('_');
	var region = fields[0];
	var year = fields[1];

	var regionSum = {
		//_id : 0,
		region: region,
		year: parseInt(year),
		number: 0
	}	

	values.forEach( function(value) {
		regionSum.number += value.number
	});

	return regionSum;
};

db.country_of_birth.mapReduce(mapRename, reduceSumRegion, {out:'mig_vol_by_region'});

//flatten the values
db.mig_vol_by_region.find().forEach(function(res){
	db.mig_vol_by_region.update({_id: res._id}, res.value)
}) 


// Now just run this thru mongo shell : mongo < cob.js
