function check_valid(item)
{
	var phone = /^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$/;
	var email = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	var x = document.getElementsById(item);
	var err = document.getElementsById("err");
	if (item == "phone") {
			if (phone.test(x)) {
				return true;
		}
		else {
			err.innerHTML = "phone number is not valid, please input again.";
			return false;
		}
	}
	if (item == "email") {
		if (email.test(x)) {
			return true;
		}
		else {
			err.innerHTML = "email is not valid, please input again."
			return false;
		}
	}
	var space = /\s/g;
	if (x.match(space)) {
		err.innerHTML = "no space is allowed!"
		return false;
	}
	else return true;
}
