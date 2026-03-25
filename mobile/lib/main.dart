import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Potato Disease Detection',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: Colors.green,
        useMaterial3: true,
      ),
      home: const HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  File? _image;
  final ImagePicker _picker = ImagePicker();
  bool _isLoading = false;
  String? _predictedClass;
  String? _rawClass;
  double? _confidence;
  String? _error;
  bool _isLoadingTreatment = false;
  String? _treatment;

  // Production URL — set to your VPS IP or domain
  // For local dev: Android emulator uses 10.0.2.2, iOS simulator uses localhost
  static const String productionUrl = 'https://plantdisease.thinkverseai.ca/api';
  static const bool isProduction = bool.fromEnvironment('PRODUCTION', defaultValue: false);

  String get baseUrl {
    if (isProduction) return productionUrl;
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://localhost:8000';
  }

  Future<void> _pickImage(ImageSource source) async {
    final pickedFile = await _picker.pickImage(source: source);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _predictedClass = null;
        _rawClass = null;
        _confidence = null;
        _error = null;
        _treatment = null;
      });
    }
  }

  Future<void> _predict() async {
    if (_image == null) return;

    setState(() {
      _isLoading = true;
      _error = null;
      _predictedClass = null;
      _rawClass = null;
      _confidence = null;
      _treatment = null;
    });

    try {
      final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/predict'));
      request.files
          .add(await http.MultipartFile.fromPath('file', _image!.path));

      final streamedResponse = await request.send().timeout(
            const Duration(seconds: 30),
          );
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _rawClass = data['class'] as String;
          _predictedClass = _rawClass!
              .replaceAll('Potato___', '')
              .replaceAll('_', ' ');
          _confidence = (data['confidence'] as num).toDouble();
        });
      } else {
        setState(() {
          _error = 'Prediction failed (${response.statusCode})';
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Could not connect to server. Make sure the API is running.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _fetchTreatment() async {
    if (_rawClass == null) return;

    setState(() {
      _isLoadingTreatment = true;
    });

    try {
      final response = await http
          .get(Uri.parse('$baseUrl/treatment/$_rawClass'))
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _treatment = data['treatment'] as String;
        });
      } else {
        setState(() {
          _treatment = 'Failed to load treatment information.';
        });
      }
    } catch (e) {
      setState(() {
        _treatment = 'Could not connect to server.';
      });
    } finally {
      setState(() {
        _isLoadingTreatment = false;
      });
    }
  }

  void _showPickerOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Take Photo'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Choose from Gallery'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Potato Disease Detection'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            GestureDetector(
              onTap: _showPickerOptions,
              child: Container(
                height: 300,
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _image != null ? Colors.green : Colors.grey[300]!,
                    width: 2,
                    strokeAlign: BorderSide.strokeAlignInside,
                  ),
                ),
                child: _image != null
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(14),
                        child: Image.file(
                          _image!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                        ),
                      )
                    : const Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.add_a_photo,
                              size: 64, color: Colors.grey),
                          SizedBox(height: 12),
                          Text(
                            'Tap to select an image',
                            style:
                                TextStyle(color: Colors.grey, fontSize: 16),
                          ),
                        ],
                      ),
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _image != null && !_isLoading ? _predict : null,
              icon: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.search),
              label: Text(_isLoading ? 'Predicting...' : 'Predict Disease'),
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                textStyle: const TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w600),
              ),
            ),
            if (_predictedClass != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.green[200]!),
                ),
                child: Column(
                  children: [
                    const Text(
                      'Prediction',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _predictedClass!,
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Colors.green[800],
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Confidence: ${_confidence!.toStringAsFixed(1)}%',
                      style: const TextStyle(
                          fontSize: 15, color: Colors.black54),
                    ),
                    if (_treatment == null) ...[
                      const SizedBox(height: 16),
                      OutlinedButton.icon(
                        onPressed: _isLoadingTreatment ? null : _fetchTreatment,
                        icon: _isLoadingTreatment
                            ? const SizedBox(
                                width: 16,
                                height: 16,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.medical_services_outlined),
                        label: Text(_isLoadingTreatment
                            ? 'Loading...'
                            : 'View Treatment'),
                      ),
                    ],
                    if (_treatment != null) ...[
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 8),
                      const Text(
                        'Treatment',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _treatment!,
                        style: const TextStyle(fontSize: 15, height: 1.4),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ],
                ),
              ),
            ],
            if (_error != null) ...[
              const SizedBox(height: 24),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.red[50],
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.red[200]!),
                ),
                child: Text(
                  _error!,
                  style: TextStyle(color: Colors.red[800], fontSize: 14),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
