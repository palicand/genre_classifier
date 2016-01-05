/**
 * Created by palickaa on 04/01/16.
 */
var React = require("react");
var Dropzone = require("react-dropzone");
var ReactDOM = require('react-dom');
var request = require('superagent');
var ReactHighcharts = require('react-highcharts');

var SubmitForm = React.createClass({
    onDrop: function (files) {
        console.log('Received files: ', files);
        var req = request.post('/api/process_file');
        files.forEach((file) => {
            req.attach(file.name, file);
        });
        req.set('Accept', 'application/json');
        var self = this;
        req.end((err, res) => {
            console.log(err);
            console.log(res);
            self.props.onDataReturn(res.body)
        });
    },
    render: function () {
        return (
            <div id="dropzone">
                <Dropzone onDrop={this.onDrop}>
                    <div>Try dropping some files here, or click to select files
                        to upload.
                    </div>
                </Dropzone>
            </div>
        );
    }
});

var Result = React.createClass({
    getDefaultProps: function () {
        return {
            classes: []
        };
    },
    render: function () {
        this.props.classes.sort((a, b) => {
            var valueLeft = a[1], valueRight = b[1];
            if(valueLeft > valueRight) {
                return -1;
            } else if(valueLeft < valueRight) {
                return 1;
            } else {
                return 0;
            }
        });
        return (
            <div id="predictions">
                <h2>Predicted classes</h2>
                <ol>
                    {this.props.classes.map((predicted) => {
                        return <li key={predicted[0]}>{predicted[0]}
                            - {predicted[1]}</li>;
                    })}
                </ol>
            </div>
        );
    }
});

var Application = React.createClass({

    getInitialState: function () {
        return {
            classes: [],
            amplitude: [],
        };
    },
    onDataReturn: function (data) {
        this.setState({
            classes: data.prediction,
            amplitude: data.amplitude
        });
    },
    render: function () {
        var options = {
            series: [{
                name: "Amplitude",
                data: this.state.amplitude
            }
            ]
        };
        return (<div>
            <SubmitForm onDataReturn={this.onDataReturn}/>
            <Result classes={this.state.classes}/>
            <ReactHighcharts config={options} ref="chart"/>
        </div>)
    }
});

ReactDOM.render(
    <Application/>,
    document.getElementById('main')
);