function checkph()
{
	var phone = /^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$/;
	x = document.getElementById("ph");
	if (phone.test(x.value)) {
		document.getElementById("pherr").innerHTML = "ok";
		document.getElementById("pherr").style.color = "green";
	}
	else {
		document.getElementById("pherr").innerHTML = "not valid phone";
		document.getElementById("pherr").style.color = "red";
	}
}
function checkemail()
{
	var email = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	x = document.getElementById("email");
	em = document.getElementById("emerr");
	if (email.test(x.value)) {
		em.innerHTML = "ok";
		em.style.color = "green";
	}
	else {
		em.innerHTML = "not valid email";
		em.style.color = "red";
	}
}
function hasWhiteSpace(s) {
  return /\s/g.test(s);
}
function checkpwd()
{
	x = document.getElementById("pwd");
	pw = document.getElementById("pwderr");
	if (hasWhiteSpace(x.value)) {
		pw.innerHTML = "space is not allowed";
		pw.style.color = "red";
	}
	else{
		if (x.value.length < 8) {
			pw.innerHTML = "too weak";
			pw.style.color = "red";
		}
		else {
			pw.innerHTML = "ok";
			pw.style.color = "green";
		}
	}
}
function checkusr()
{
	x = document.getElementById("usr");
	us = document.getElementById("uerr");
	if (hasWhiteSpace(x.value)) {
		us.innerHTML = "space is not allowed";
		us.style.color = "red";
	}
	else {
		us.innerHTML = "ok";
		us.style.color = "green";
	}
}
function checkloc()
{
	loc = document.getElementById("locerr");
	loc.innerHTML = "ok";
	loc.style.color = "green";
}
function checkallok()
{
	var form = document.getElementById("form");
	us = document.getElementById("uerr");
	loc = document.getElementById("locerr");
	ph = document.getElementById("pherr");
	email = document.getElementById("emerr");
	pw = document.getElementById("pwderr");
	if (us.style.color == "green" && loc.style.color == "green" &&
			ph.style.color == "green" && email.style.color == "green" &&
			pw.style.color == "green") {
		form.submit()
	}
	else {
		err = document.getElementById("err");
		err.innerHTML = "Some infos are not valid, please fill them in.";
	}
}

function ch()
{
  var x = document.getElementById("pherr");
  var form = document.getElementById("form");
  if (x.style.color == "green"){
    form.submit();
  }
}
