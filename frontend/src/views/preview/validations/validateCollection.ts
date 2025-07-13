import Joi from 'joi'

export const validateCollection = (reviewName: string) => {
  return Joi.string()
    .required()
    .max(150)
    .messages({
      'string.base': 'Dataset/Review name must be a string',
      'string.empty': 'Dataset/Review name is required',
      'string.max': 'Dataset/Review name must be less than 150 characters',
      'any.required': 'Dataset/Review name is required',
    })
    .validate(reviewName)
}
