import numpy as np


BGR_COMMON = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'yellow': (0, 255, 255),
    'bright_green': (0, 255, 102)
}


PITCH0 = {
    'plate': {
        'min': np.array((60.0, 72.0, 38.0)),
        'max': np.array((86.0, 136.0, 255.0)),
        'contrast': 100.0,
        'blur': 7
    },
    'dot': [{
        'min': np.array((16.0, 39.0, 55.0)),
        'max': np.array((68.0, 125.0, 78.0)),
        'contrast': 5.0,
        'blur': 5
    },
    {
        'min': np.array((16.0, 39.0, 55.0)),
        'max': np.array((68.0, 125.0, 78.0)),
        'contrast': 5.0,
        'blur': 5
    }],
    'red': [
        {
            'min': np.array((0.0, 114.0, 132.0)),
            'max': np.array((5.0, 255.0, 255.0)),
            'contrast': 30.0,
            'blur': 5
        },
        {
            'min': np.array((0.0, 181.0, 130.0)),
            'max': np.array((10.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 10
        }
    ],
    'yellow': [
        {
            'min': np.array((16.0, 165.0, 136.0)), #LH,LS,LV
            'max': np.array((19.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((0.0, 193.0, 137.0)), #LH,LS,LV
            'max': np.array((50.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((6.0, 154.0, 229.0)), #LH,LS,LV
            'max': np.array((130.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((10.0, 210.0, 162.0)), #LH,LS,LV
            'max': np.array((20.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        }
    ],
    'blue': [
        {
            'min': np.array((88.0, 147.0, 82.0)),    #LH,LS,LV
            'max': np.array((104.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 0.0,
            'blur': 0
        },
        {
            'min': np.array((87.0, 147.0, 82.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {
            'min': np.array((87.0, 105.0, 82.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {
            'min': np.array((87.0, 100.0, 90.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {	#not too good at edges.
            'min': np.array((80.0, 59.0, 90.0)),	#LH,LS,LV
            'max': np.array((135.0, 142.0, 190.0)),	#UH,US,UV
            'contrast': 1.0,
            'blur': 1
        },
        {   #not too good at edges.
            'min': np.array((80.0, 120.0, 80.0)),    #LH,LS,LV
            'max': np.array((163.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
	{
            'min': np.array((83.0, 69.0, 173.0)),
            'max': np.array((161.0, 211.0, 194.0)),
            'contrast': 100.0,
            'blur': 14
        }

    ]
    # (np.array((91.0, 118.0, 90.0)), np.array((169.0, 255.0, 255.0)), 1.0, 1)
}

PITCH1 = {
    'plate': {
        'min': np.array((41.0, 63.0, 183.0)),
        'max': np.array((60.0, 255.0, 255.0)),
        'contrast': 100.0,
        'blur': 0
    },
    'dot': [{
	'min': np.array((66.0, 84.0, 61.0)),
        'max': np.array((117.0, 163.0, 76.0)),
        'contrast': 9.0,
        'blur': 4
	},
	{
        'min': np.array((16.0, 39.0, 55.0)),
        'max': np.array((68.0, 125.0, 78.0)),
        'contrast': 5.0,
        'blur': 5
    }],
    'red': [
        {
            'min': np.array((0.0, 114.0, 250.0)),
            'max': np.array((5.0, 255.0, 255.0)),
            'contrast': 100.0,
            'blur': 5
        },
        {
            'min': np.array((0.0, 181.0, 130.0)),
            'max': np.array((10.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 10
        }
    ],
    'yellow': [
        {
            'min': np.array((7.0, 176.0, 195.0)), #LH,LS,LV
            'max': np.array((22.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((0.0, 193.0, 137.0)), #LH,LS,LV
            'max': np.array((50.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((6.0, 154.0, 229.0)), #LH,LS,LV
            'max': np.array((130.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        },
        {
            'min': np.array((10.0, 210.0, 162.0)), #LH,LS,LV
            'max': np.array((20.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        }
    ],
    'blue': [
        {
            'min': np.array((74.0, 5.0, 77.0)),    #LH,LS,LV
            'max': np.array((99.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 0.0,
            'blur': 0
        },
        {
            'min': np.array((87.0, 147.0, 82.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {
            'min': np.array((87.0, 105.0, 82.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {
            'min': np.array((87.0, 100.0, 90.0)),
            'max': np.array((104.0, 255.0, 255.0)),
            'contrast': 1.0,
            'blur': 1
        },
        {   #not too good at edges.
            'min': np.array((80.0, 59.0, 90.0)),    #LH,LS,LV
            'max': np.array((135.0, 142.0, 190.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 1
        },
        {   #not too good at edges.
            'min': np.array((80.0, 120.0, 80.0)),    #LH,LS,LV
            'max': np.array((163.0, 255.0, 255.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
        }

    ]
    # (np.array((91.0, 118.0, 90.0)), np.array((169.0, 255.0, 255.0)), 1.0, 1)
}

KMEANS0 = {'yellow': [
            {
            'min': np.array((16.0, 190.0, 136.0)), #LH,LS,LV
            'max': np.array((19.0, 255.0, 200.0)), #UH,US,UV
            'contrast': 1.0,
            'blur': 0
            }],
          'blue': [
            {
            'min': np.array((88.0, 160.0, 86.0)),    #LH,LS,LV
            'max': np.array((104.0, 190.0, 106.0)), #UH,US,UV
            'contrast': 0.0,
            'blur': 0
            }]
        }