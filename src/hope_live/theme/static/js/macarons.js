/*
* Licensed to the Apache Software Foundation (ASF) under one
* or more contributor license agreements.  See the NOTICE file
* distributed with this work for additional information
* regarding copyright ownership.  The ASF licenses this file
* to you under the Apache License, Version 2.0 (the
* "License"); you may not use this file except in compliance
* with the License.  You may obtain a copy of the License at
*
*   http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied.  See the License for the
* specific language governing permissions and limitations
* under the License.
*/

(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['exports', 'echarts'], factory);
    } else if (
        typeof exports === 'object' &&
        typeof exports.nodeName !== 'string'
    ) {
        // CommonJS
        factory(exports, require('echarts/lib/echarts'));
    } else {
        // Browser globals
        factory({}, root.echarts);
    }
})(this, function(exports, echarts) {
    var log = function(msg) {
        if (typeof console !== 'undefined') {
            console && console.error && console.error(msg);
        }
    };
    if (!echarts) {
        log('ECharts is not Loaded');
        return;
    }

    var colorPalette = [
        '#00AEEF',
        '#0047BB',
        '#004C45',
        '#FFB500',
        '#FF7100',
        '#9ADBE8',
        '#66CBF4',
        '#4D8FD6',
        '#007A6E',
        '#FFD466',
        '#FFA64D',
        '#C7EBF4',
        '#BDBDBD',
        '#BDBDBD',
        '#E2231A',
        '#004C45',
        '#00AEEF',
        '#0047BB',
        '#FFB500',
        '#FF7100'
    ];

    var theme = {
        color: colorPalette,
        textStyle: {
            fontFamily: '"Noto Sans", "Noto Sans Arabic", "Noto Sans SC", sans-serif'
        },

        title: {
            textStyle: {
                fontWeight: 'normal',
                color: '#0047BB'
            }
        },

        visualMap: {
            itemWidth: 15,
            color: ['#00AEEF', '#9ADBE8']
        },

        toolbox: {
            iconStyle: {
                borderColor: colorPalette[0]
            }
        },

        tooltip: {
            borderWidth: 0,
            backgroundColor: 'rgba(50,50,50,0.5)',
            textStyle: {
                color: '#FFF'
            },
            axisPointer: {
                type: 'line',
                lineStyle: {
                    color: '#0047BB'
                },
                crossStyle: {
                    color: '#0047BB'
                },
                shadowStyle: {
                    color: 'rgba(0,0,0,0.08)'
                }
            }
        },

        dataZoom: {
            dataBackgroundColor: '#E6F7FD',
            fillerColor: 'rgba(0,71,187,0.15)',
            handleColor: '#0047BB'
        },

        grid: {
            borderColor: 'rgba(0,0,0,0.08)'
        },

        categoryAxis: {
            axisLine: {
                lineStyle: {
                    color: '#0047BB'
                }
            },
            splitLine: {
                lineStyle: {
                    color: ['rgba(0,0,0,0.08)']
                }
            }
        },

        valueAxis: {
            axisLine: {
                lineStyle: {
                    color: '#0047BB'
                }
            },
            splitArea: {
                show: true,
                areaStyle: {
                    color: ['rgba(250,250,250,0.1)', 'rgba(200,200,200,0.1)']
                }
            },
            splitLine: {
                lineStyle: {
                    color: ['rgba(0,0,0,0.08)']
                }
            }
        },

        timeline: {
            lineStyle: {
                color: '#0047BB'
            },
            controlStyle: {
                color: '#0047BB',
                borderColor: '#0047BB'
            },
            symbol: 'emptyCircle',
            symbolSize: 3
        },

        line: {
            smooth: true,
            symbol: 'emptyCircle',
            symbolSize: 3
        },

        candlestick: {
            itemStyle: {
                color: '#FF7100',
                color0: '#00AEEF'
            },
            lineStyle: {
                width: 1,
                color: '#FF7100',
                color0: '#00AEEF'
            },
            areaStyle: {
                color: '#00AEEF',
                color0: '#0047BB'
            }
        },

        scatter: {
            symbol: 'circle',
            symbolSize: 4
        },

        map: {
            itemStyle: {
                color: '#ddd'
            },
            areaStyle: {
                color: '#FFA64D'
            },
            label: {
                color: '#FF7100'
            }
        },

        graph: {
            itemStyle: {
                color: '#FF7100'
            },
            linkStyle: {
                color: '#00AEEF'
            }
        },

        gauge: {
            axisLine: {
                lineStyle: {
                    color: [
                        [0.2, '#00AEEF'],
                        [0.8, '#00AEEF'],
                        [1, '#FF7100']
                    ],
                    width: 10
                }
            },
            axisTick: {
                splitNumber: 10,
                length: 15,
                lineStyle: {
                    color: 'auto'
                }
            },
            splitLine: {
                length: 22,
                lineStyle: {
                    color: 'auto'
                }
            },
            pointer: {
                width: 5
            }
        }
    };

    echarts.registerTheme('macarons', theme);
});
