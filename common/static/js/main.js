$('.place-item').hover(
    function () {
        $(this).addClass('active')
    },
    function () {
        $(this).removeClass('active')
    }
);

function _(id) {
    return document.getElementById(id);
}

var droppedIn = false;

function drag_start(event) {
    event.dataTransfer.dropEffect = "move";
    event.dataTransfer.setData("text", event.target.getAttribute('id'));
}

function drag_enter(event) {
}

function drag_leave(event) {
}

function drag_drop(event) {
    event.preventDefault();
    /* Prevent undesirable default behavior while dropping */
    var elem_id = event.dataTransfer.getData("text");
    event.target.appendChild(_(elem_id));
    droppedIn = true;
}

function drag_end(event) {
    droppedIn = false;
}

function readDropZone() {
    let dict = {};
    for (let i = 0; i < _("drop_zone").children.length; i++) {
        user_id = $(_("drop_zone").children[i]).attr('data-id');
        dict[user_id] = user_id;
    }

    $.ajax({
        type: "POST",
        url: "/common/suggest/",
        data: dict,
        dataType: 'html',
        success: function (data) {

            console.log(data);

            show_loader();
            setTimeout(function () {
                console.log(data.indexOf('exampleModal'));

                if (data.indexOf('exampleModal') === -1) {
                    delaySuccess(data);
                } else {
                    delayError(data);
                }
            }, 2000);
        },
        complete: function () {
            setTimeout(function () {
                hide_loader();
            }, 2200);
        }
    });

    function show_loader() {
        $('.ajax-loader').css("visibility", "visible");
    }

    function hide_loader() {
        $('.ajax-loader').css("visibility", "hidden");
    }

    function delaySuccess(data) {
        console.log("OK");
        loadGraphicData();
        $("#ajax-data").html(data);
        myFunction();
    }

    function delayError(data) {
        console.log("ERROR");
        $("#ajax-data").html(data);

        $("#exampleModal").modal('show');
    }


    function loadGraphicData() {
        var endpoint = '/common/suggest_data/';
        $.ajax({
            method: "GET",
            url: endpoint,
            success: function (data) {
                //labels = data.labels;
                //defaultData = data.default;
                setChart(data.default, data.labels)
            },
            error: function (error_data) {
                console.log("error");
                console.log(error_data)
            }
        });

        function setChart(defaultData, labels) {
            var ctx = document.getElementById("myChart");
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '',
                        data: defaultData,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.8)',
                            'rgba(54, 162, 235, 0.8)',
                            'rgba(255, 206, 86, 0.8)',
                            'rgba(75, 192, 192, 0.8)',
                            'rgba(153, 102, 255, 0.8)',
                            'rgba(255, 159, 64, 0.8)'
                        ],
                        borderColor: [
                            'rgba(255,99,132,1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {

                    legend: {
                        display: false,
                    },
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]
                    }
                }
            });
        }

    }
}

function myFunction() {
    var x = document.getElementById("toggle-data");
    var y = document.getElementById("ajax-data");

    if (x.style.display === "none") {
        x.style.display = "block";
        y.style.display = "none";
    } else {
        x.style.display = "none";
        y.style.display = "block";
    }
}


$("suggest-button").click(function () {
    $('html,body').animate({
            scrollTop: $("#ajax-data").offset().top
        },
        2000);
});

if (document.getElementById('place-data')) {

    loadGraphicData();

    function loadGraphicData() {
        var endpoint = '/common/user_place_data/';
        $.ajax({
            method: "GET",
            url: endpoint,
            success: function (data) {
                //labels = data.labels;
                //defaultData = data.default;
                setChart(data.default, data.labels)
            },
            error: function (error_data) {
                console.log("error");
                console.log(error_data)
            }
        });

        function setChart(defaultData, labels) {
            var ctx2 = document.getElementById("place-data");
            var myChart = new Chart(ctx2, {

                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '',
                        data: defaultData,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 159, 64, 0.7)'
                        ],
                        borderColor: [
                            'rgba(255,99,132,1)',
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    legend: {
                        position: 'bottom',
                        fullWidth: 'true',
                        labels: {}
                    }
                }
            });
        }
    }

}







