from fastapi import FastAPI, HTTPException, Depends


import schemas


app = FastAPI()


@app.post('/generate', response_model=schemas.SecretKeyResponse)
async def generate_secret(
    secret: schemas.SecretCreate
):
    '''Generate secret key for a one-time secret.'''
    pass

