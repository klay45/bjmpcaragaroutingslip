$(document).ready(function(){
	$('.decrement-btn').click(function(e){
        e.preventDefault();
        var dec_value = $(this).closest('.product_data').find('.qty-input').val();
        var value = parseInt(dec_value,10);
        value = isNaN(value) ? 0 : value;
        if(value > 1)
        {
            value--;
            $(this).closest('.product_data').find('.qty-input').val(value);
        }
    });

    $('.increment-btn').click(function(e){
        e.preventDefault();

        var inc_value = $(this).closest('.product_data').find('.qty-input').val();
        var value = parseInt(inc_value,10);
        value = isNaN(value) ? 0 : value;
        if(value < 10)
        {
            value++;
            $(this).closest('.product_data').find('.qty-input').val(value);
        }
    });

    $('.addToCartBtn').click(function (e){
    	e.preventDefault();
    	var product_id = $(this).closest('.product_data').find('.prod_id').val();
    	var product_qty= $(this).closest('.product_data').find('.qty-input').val();
    	var token = $('input[name=csrfmiddlewaretoken]').val();
       
    	$.ajax({
    		method: "POST",
    		url: "addtocart/",
    		data: {
    			'product_id':product_id,
    			'product_qty': product_qty,
    			csrfmiddlewaretoken: token
    		},

    		success: function (response) {
    			console.log(response)
                alertify.set('notifier','position', 'top-left');
    			alertify.success(response.status)
                



    		}
    	});
    });


    $('.dddd').click(function (e){
        e.preventDefault();
        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            method: "POST",
            url: "addtowishlist/",
            data: {
                'product_id':product_id,
                csrfmiddlewaretoken: token
            },
            success: function (response) {
                console.log(response)
                alertify.set('notifier','position', 'top-left');
                alertify.success(response.status)


               
            }
        });

    });    

    /*for checkout razor pay*/





    $('.cgff').click(function (e){
        e.preventDefault();
        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var product_qty= $(this).closest('.product_data').find('.qty-input').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();
       
        $.ajax({
            method: "POST",
            url: "updatecart/",
            data: {
                'product_id':product_id,
                'product_qty': product_qty,
                csrfmiddlewaretoken: token
            },

            success: function (response) {
                console.log(response)
                alertify.set('notifier','position', 'top-left');
                alertify.success(response.status)
                



            }
        });
    });


    
    $('.delete-cart-item').click(function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            method: "POST",
            url: "deletecart/",
            data: {
                'product_id':product_id,
                csrfmiddlewaretoken: token
            },
            success: function (response) {
                console.log(response)
                alertify.set('notifier','position', 'top-left');
                alertify.success(response.status)
                $('.cartdata').load(location.href + " .cartdata")
            }

        });


    });


    $(document).on('click','.delet-wishlist-item', function(e){
        e.preventDefault();

        var product_id = $(this).closest('.product_data').find('.prod_id').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            method: "POST",
            url: "deletewishlist/",
            data: {
                'product_id':product_id,
                csrfmiddlewaretoken: token
            },
            success: function (response) {
                console.log(response)
                alertify.set('notifier','position', 'top-left');
                alertify.success(response.status)
                $('.wishdata').load(location.href + " .wishdata")
            }

        });


    });





    
    $('.payWithRazorPay').click(function(e){
        e.preventDefault();
        var fname = $("[name='fname']").val();
        var lname = $("[name='lname']").val();
        var phone = $("[name='phone']").val();
        var email = $("[name='email']").val();
        var address = $("[name='address']").val();
        var city = $("[name='city']").val();
        var region = $("[name='region']").val();
        var zipcode = $("[name='zipcode']").val();
        var token = $("[name='csrfmiddlewaretoken']").val();

        if (fname == "" || lname == "" || phone == "" || email == "" || address == "" || city == "" || region == "" || zipcode == "")
        {
         
            swal("Alert", "All fields are mandatory", "error");
            return false;
        }
        else
        {

            $.ajax({
            method: "GET",
            url: "proceedtopay/",

            success: function (response) {
                //console.log(response)
                /*alertify.set('notifier','position', 'top-left');
                alertify.success(response.status)*/
                var options = {
                    "key": "rzp_test_fBxBroRIsDfgen", // Enter the Key ID generated from the Dashboard
                    "amount": response.total_price * 100,  // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
                    "currency": "INR",
                    "name": "klay45 Corp",
                    "description": "Thank you for Buying",
                    "image": "https://example.com/your_logo",
                   // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                    "handler": function (response){

                        alert(response.razorpay_payment_id);
                        data = {
                            "fname": fname,
                            "lname": lname,
                            "email": email,
                            "phone": phone,
                            "address": address,
                            "city": city,
                            "region": region,
                            "zipcode": zipcode,
                            "payment_mode": "Paid by Razor Pay",
                            "payment_id": response.razorpay_payment_id,
                            csrfmiddlewaretoken: token
                        }
                        $.ajax({
                            method: "POST",
                            url: "placeorder/",
                            data: data,
                            success: function (response) {
                                console.log(response)
                                swal("Congratulation!", response.status,"success").then((value) => {
                                    window.location.href ="myorder/"
                                });
                            }
                        

                        });

                    },
                    "prefill": {
                        "name": fname+ " "+lname,
                        "email": email,
                        "contact": phone
                    },
                    "notes": {
                        "address": "Razorpay Corporate Office"
                    },
                    "theme": {
                        "color": "#3399cc"
                    }
            };
                var rzp1 = new Razorpay(options);
 
                rzp1.open();
               
                }

            });



            /*var options = {
            "key": "YOUR_KEY_ID", // Enter the Key ID generated from the Dashboard
            "amount": "50000", // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
            "currency": "INR",
            "name": "Acme Corp",
            "description": "Test Transaction",
            "image": "https://example.com/your_logo",
            "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
            "handler": function (response){
                alert(response.razorpay_payment_id);
                alert(response.razorpay_order_id);
                alert(response.razorpay_signature)
            },
            "prefill": {
                "name": "Gaurav Kumar",
                "email": "gaurav.kumar@example.com",
                "contact": "9999999999"
            },
            "notes": {
                "address": "Razorpay Corporate Office"
            },
            "theme": {
                "color": "#3399cc"
            }
        };
            var rzp1 = new Razorpay(options);
 
            rzp1.open();*/
        }

    });

});