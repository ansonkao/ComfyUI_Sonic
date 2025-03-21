import torch
import torch.nn as nn

backwarp_tenGrid = {}


def warp(tenInput, tenFlow):
    if torch.backends.mps.is_available():
        device = torch.device("cpu")
        tenInput = tenInput.cpu()
        tenFlow = tenFlow.cpu()
    else:
        device = tenFlow.device
    k = (str(tenFlow.device), str(tenFlow.size()))
    if k not in backwarp_tenGrid:
        tenHorizontal = torch.linspace(-1.0, 1.0, tenFlow.shape[3], device=device).view(
            1, 1, 1, tenFlow.shape[3]).expand(tenFlow.shape[0], -1, tenFlow.shape[2], -1)
        tenVertical = torch.linspace(-1.0, 1.0, tenFlow.shape[2], device=device).view(
            1, 1, tenFlow.shape[2], 1).expand(tenFlow.shape[0], -1, -1, tenFlow.shape[3])
        backwarp_tenGrid[k] = torch.cat(
            [tenHorizontal, tenVertical], 1).to(device)

    tenFlow = torch.cat([tenFlow[:, 0:1, :, :] / ((tenInput.shape[3] - 1.0) / 2.0),
                         tenFlow[:, 1:2, :, :] / ((tenInput.shape[2] - 1.0) / 2.0)], 1)

    g = (backwarp_tenGrid[k] + tenFlow).permute(0, 2, 3, 1)
    result=torch.nn.functional.grid_sample(input=tenInput, grid=g, mode='bilinear', padding_mode='border', align_corners=True)
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        result = result.to('mps')
        #return torch.nn.functional.grid_sample(input=tenInput, grid=g, mode='bilinear', padding_mode='zeros', align_corners=True)
    return result
