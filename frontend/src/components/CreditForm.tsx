import React, { useState } from 'react';
import { Calculator, Upload, FileText, X } from 'lucide-react';

interface DocumentFiles {
  pdfFile: File | null;
  gstFile: File | null;
  bankFile: File | null;
}

interface CreditFormProps {
  onSuccess?: (result: any) => void;
}

const CreditForm: React.FC<CreditFormProps> = ({ onSuccess }) => {
  const [documentFiles, setDocumentFiles] = useState<DocumentFiles>({
    pdfFile: null,
    gstFile: null,
    bankFile: null,
  });

  const [officerNotes, setOfficerNotes] = useState('');
  const [applicantName, setApplicantName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (fileType: keyof DocumentFiles, file: File | null) => {
    setDocumentFiles(prev => ({
      ...prev,
      [fileType]: file
    }));
  };

  const removeFile = (fileType: keyof DocumentFiles) => {
    setDocumentFiles(prev => ({
      ...prev,
      [fileType]: null
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('applicant_name', applicantName);
      formDataToSend.append('officer_notes', officerNotes);

      if (documentFiles.pdfFile) {
        formDataToSend.append('pdf_file', documentFiles.pdfFile);
      }
      if (documentFiles.gstFile) {
        formDataToSend.append('gst_file', documentFiles.gstFile);
      }
      if (documentFiles.bankFile) {
        formDataToSend.append('bank_file', documentFiles.bankFile);
      }

      const response = await fetch('/api/process-application', {
        method: 'POST',
        body: formDataToSend,
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        const msg = errorBody.error || errorBody.message || 'Failed to process documents';
        throw new Error(msg);
      }

      const data = await response.json();
      console.log('Document processing result:', data);
      onSuccess?.(data.result || data);
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Error processing request. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const FileUpload: React.FC<{
    label: string;
    fileType: keyof DocumentFiles;
    accept: string;
    icon: React.ReactNode;
  }> = ({ label, fileType, accept, icon }) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {icon}
        {label}
      </label>
      <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-blue-400 transition-colors">
        <div className="space-y-1 text-center">
          {documentFiles[fileType] ? (
            <div className="flex items-center justify-center">
              <FileText className="w-8 h-8 text-blue-600 mr-2" />
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">
                  {documentFiles[fileType]?.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(documentFiles[fileType]?.size! / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                type="button"
                onClick={() => removeFile(fileType)}
                className="ml-2 text-red-500 hover:text-red-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <>
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="flex text-sm text-gray-600">
                <label
                  htmlFor={fileType}
                  className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none"
                >
                  <span>Upload {label.toLowerCase()}</span>
                  <input
                    id={fileType}
                    name={fileType}
                    type="file"
                    accept={accept}
                    className="sr-only"
                    onChange={(e) => handleFileChange(fileType, e.target.files?.[0] || null)}
                  />
                </label>
              </div>
              <p className="text-xs text-gray-500">or drag and drop</p>
            </>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <Calculator className="w-8 h-8 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900">Document Upload</h2>
        <p className="text-gray-600 mt-2">Upload your financial documents for credit assessment</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Applicant Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Applicant Name
            </label>
            <input
              type="text"
              value={applicantName}
              onChange={(e) => setApplicantName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter applicant name"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Officer Notes
            </label>
            <textarea
              value={officerNotes}
              onChange={(e) => setOfficerNotes(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Additional notes from credit officer"
            />
          </div>
        </div>

        {/* Document Upload Form */}
        <div className="space-y-6">
          <FileUpload
            label="Financial PDF"
            fileType="pdfFile"
            accept=".pdf"
            icon={<FileText className="w-5 h-5 inline mr-2" />}
          />
          <FileUpload
            label="GST CSV"
            fileType="gstFile"
            accept=".csv"
            icon={<FileText className="w-5 h-5 inline mr-2" />}
          />
          <FileUpload
            label="Bank Statement CSV"
            fileType="bankFile"
            accept=".csv"
            icon={<FileText className="w-5 h-5 inline mr-2" />}
          />
        </div>

        <div className="flex justify-center pt-6">
          <button
            type="submit"
            disabled={isLoading}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center text-lg font-medium"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                Processing Documents...
              </>
            ) : (
              'Process Documents & Analyze'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreditForm;