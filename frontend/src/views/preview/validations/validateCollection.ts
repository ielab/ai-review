import Joi from 'joi'

export const validateCollection = (collectionName: string) => {
  return Joi.string()
    .required()
    .max(150)
    .messages({
      'string.base': 'Collection name must be a string',
      'string.empty': 'Collection name is required',
      'string.max': 'Collection name must be less than 150 characters',
      'any.required': 'Collection name is required',
    })
    .validate(collectionName)
}
