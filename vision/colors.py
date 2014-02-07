import numpy as np


PITCH0 = {
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
        }

    ]
    # (np.array((91.0, 118.0, 90.0)), np.array((169.0, 255.0, 255.0)), 1.0, 1)
}

PITCH1 = {
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