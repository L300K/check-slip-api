import os
import shutil
import time

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from check_slip import checkSlip

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/api/slip")
def check_slip(img: UploadFile = File(...)):
    if img.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Only JPG or PNG images are allowed")

    filename = f'utils/slip/{img.filename}'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(img.file, buffer)

    start_time = time.time()
    load_dotenv('.env')
    slip = checkSlip()
    slip.get_slip_data(slip_path=filename, max_retries=2)
    os.remove(filename)
    end_time = time.time()
    elapsed_time = end_time - start_time

    if slip.slip_data['message'] == 'Slip not found.':
        return JSONResponse(
            status_code=404,
            content=slip.slip_data
        )

    return JSONResponse(content={"slip_data": slip.slip_data, "elapsed_time": f'{elapsed_time:.2f} seconds'})
