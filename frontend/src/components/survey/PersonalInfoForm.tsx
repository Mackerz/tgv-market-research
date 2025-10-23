"use client";

import { useState } from "react";
import { ChevronDownIcon } from "@heroicons/react/24/outline";

interface PersonalInfoFormProps {
  onComplete: (
    email: string,
    phone_number: string,
    region: string,
    date_of_birth: string,
    gender: string
  ) => Promise<void>;
}

const regions = [
  { code: 'UK', name: 'United Kingdom', prefix: '+44', flag: '🇬🇧' },
  { code: 'US', name: 'United States', prefix: '+1', flag: '🇺🇸' },
  { code: 'CA', name: 'Canada', prefix: '+1', flag: '🇨🇦' },
  { code: 'AU', name: 'Australia', prefix: '+61', flag: '🇦🇺' },
  { code: 'DE', name: 'Germany', prefix: '+49', flag: '🇩🇪' },
  { code: 'FR', name: 'France', prefix: '+33', flag: '🇫🇷' },
  { code: 'ES', name: 'Spain', prefix: '+34', flag: '🇪🇸' },
  { code: 'IT', name: 'Italy', prefix: '+39', flag: '🇮🇹' },
  { code: 'NL', name: 'Netherlands', prefix: '+31', flag: '🇳🇱' },
  { code: 'SE', name: 'Sweden', prefix: '+46', flag: '🇸🇪' },
  { code: 'NO', name: 'Norway', prefix: '+47', flag: '🇳🇴' },
  { code: 'DK', name: 'Denmark', prefix: '+45', flag: '🇩🇰' },
  { code: 'FI', name: 'Finland', prefix: '+358', flag: '🇫🇮' },
];

const genders = [
  'Male',
  'Female',
  "I'd rather not say"
];

export default function PersonalInfoForm({ onComplete }: PersonalInfoFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    phone_number: '',
    region: '',
    date_of_birth: '',
    gender: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // Phone number validation
    if (!formData.phone_number) {
      newErrors.phone_number = 'Phone number is required';
    } else {
      const digitsOnly = formData.phone_number.replace(/\D/g, '');
      if (digitsOnly.length < 7 || digitsOnly.length > 15) {
        newErrors.phone_number = 'Phone number must contain 7-15 digits';
      }
    }

    // Region validation
    if (!formData.region) {
      newErrors.region = 'Please select your region';
    }

    // Date of birth validation
    if (!formData.date_of_birth) {
      newErrors.date_of_birth = 'Date of birth is required';
    } else {
      const today = new Date();
      const birthDate = new Date(formData.date_of_birth);
      const age = today.getFullYear() - birthDate.getFullYear();

      if (birthDate > today) {
        newErrors.date_of_birth = 'Birth date cannot be in the future';
      } else if (age < 13) {
        newErrors.date_of_birth = 'You must be at least 13 years old';
      } else if (age > 120) {
        newErrors.date_of_birth = 'Please enter a valid birth date';
      }
    }

    // Gender validation
    if (!formData.gender) {
      newErrors.gender = 'Please select your gender';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await onComplete(
        formData.email,
        formData.phone_number,
        formData.region,
        formData.date_of_birth,
        formData.gender
      );
    } catch (error) {
      console.error('Error submitting form:', error);
      setErrors({ submit: error instanceof Error ? error.message : 'An error occurred' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const selectedRegion = regions.find(r => r.code === formData.region);

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Personal Information</h2>
        <p className="text-gray-600">Please provide your details to begin the survey.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.email ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="your.email@example.com"
            disabled={loading}
          />
          {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
        </div>

        {/* Phone Number with Region */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Phone Number *
          </label>
          <div className="flex gap-3">
            {/* Region Selector */}
            <div className="relative">
              <select
                value={formData.region}
                onChange={(e) => handleInputChange('region', e.target.value)}
                className={`appearance-none bg-white border rounded-lg px-4 py-3 pr-10 text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.region ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              >
                <option value="" className="text-gray-500">Select Region</option>
                {regions.map((region) => (
                  <option key={region.code} value={region.code} className="text-gray-900">
                    {region.flag} {region.code} {region.prefix}
                  </option>
                ))}
              </select>
              <ChevronDownIcon className="h-5 w-5 text-gray-400 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
            </div>

            {/* Phone Number Input */}
            <input
              type="tel"
              value={formData.phone_number}
              onChange={(e) => handleInputChange('phone_number', e.target.value)}
              className={`flex-1 px-4 py-3 border rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                errors.phone_number ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Phone number"
              disabled={loading}
            />
          </div>
          {selectedRegion && (
            <p className="text-sm text-gray-500 mt-1">
              {selectedRegion.flag} {selectedRegion.name} ({selectedRegion.prefix})
            </p>
          )}
          {(errors.region || errors.phone_number) && (
            <p className="text-red-500 text-sm mt-1">
              {errors.region || errors.phone_number}
            </p>
          )}
        </div>

        {/* Date of Birth */}
        <div>
          <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 mb-2">
            Date of Birth *
          </label>
          <input
            type="date"
            id="date_of_birth"
            value={formData.date_of_birth}
            onChange={(e) => handleInputChange('date_of_birth', e.target.value)}
            className={`w-full px-4 py-3 border rounded-lg text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              errors.date_of_birth ? 'border-red-500' : 'border-gray-300'
            }`}
            max={new Date().toISOString().split('T')[0]} // Prevent future dates
            disabled={loading}
          />
          {errors.date_of_birth && <p className="text-red-500 text-sm mt-1">{errors.date_of_birth}</p>}
        </div>

        {/* Gender */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Gender *
          </label>
          <div className="space-y-2">
            {genders.map((gender) => (
              <label key={gender} className="flex items-center">
                <input
                  type="radio"
                  name="gender"
                  value={gender}
                  checked={formData.gender === gender}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  disabled={loading}
                />
                <span className="ml-3 text-gray-700">{gender}</span>
              </label>
            ))}
          </div>
          {errors.gender && <p className="text-red-500 text-sm mt-1">{errors.gender}</p>}
        </div>

        {/* Submit Button */}
        <div>
          {errors.submit && (
            <p className="text-red-500 text-sm mb-4">{errors.submit}</p>
          )}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-6 rounded-lg text-white font-medium transition-colors ${
              loading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 focus:ring-2 focus:ring-blue-500'
            }`}
          >
            {loading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Submitting...
              </div>
            ) : (
              'Continue to Survey'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}