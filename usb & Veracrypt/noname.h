///////////////////////////////////////////////////////////////////////////
// C++ code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
// http://www.wxformbuilder.org/
//
// PLEASE DO *NOT* EDIT THIS FILE!
///////////////////////////////////////////////////////////////////////////

#pragma once

#include <wx/artprov.h>
#include <wx/xrc/xmlres.h>
#include <wx/string.h>
#include <wx/stattext.h>
#include <wx/gdicmn.h>
#include <wx/font.h>
#include <wx/colour.h>
#include <wx/settings.h>
#include <wx/button.h>
#include <wx/bitmap.h>
#include <wx/image.h>
#include <wx/icon.h>
#include <wx/sizer.h>
#include <wx/listbox.h>
#include <wx/frame.h>

///////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////
/// Class MyFrame3
///////////////////////////////////////////////////////////////////////////////
class MyFrame3 : public wxFrame
{
	private:

	protected:
		wxStaticText* m_staticText9;
		wxButton* Successivo1;
		wxButton* successivo2;
		wxStaticText* m_staticText14;
		wxStaticText* m_staticText10;
		wxStaticText* m_staticText11;
		wxStaticText* m_staticText12;
		wxStaticText* m_staticText13;
		wxButton* m_button10;
		wxStaticText* m_staticText15;
		wxListBox* m_listBox2;
		wxButton* m_button13;
		wxButton* m_button14;

		// Virtual event handlers, override them in your derived class
		virtual void seipronto( wxCommandEvent& event ) { event.Skip(); }


	public:

		MyFrame3( wxWindow* parent, wxWindowID id = wxID_ANY, const wxString& title = wxEmptyString, const wxPoint& pos = wxDefaultPosition, const wxSize& size = wxSize( 693,312 ), long style = wxDEFAULT_FRAME_STYLE|wxTAB_TRAVERSAL );

		~MyFrame3();

};

